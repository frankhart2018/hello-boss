from fastapi import APIRouter, HTTPException, Request
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from datetime import datetime, timezone
import os
import json
from bson import json_util
import logging
import shutil

from ..utils.environment import OUTPUT_DIR, STATIC_DIR
from ..utils.compress import create_tarball


router = APIRouter()

logger = logging.getLogger(__name__)


IGNORE_COLLECTIONS = ["admin", "local", "config"]


def mongodb_backup(uri: str, output_dir: str) -> dict:
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(output_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)

        summary = {"databases": {}, "total_documents": 0}

        databases = client.list_database_names()
        databases = [db for db in databases if db not in ["admin", "local", "config"]]

        for db_name in databases:
            db = client[db_name]
            db_path = os.path.join(backup_path, db_name)
            os.makedirs(db_path, exist_ok=True)

            summary["databases"][db_name] = {"collections": {}}

            colls = db.list_collection_names()

            for coll_name in colls:
                collection = db[coll_name]

                docs = list(collection.find())
                doc_count = len(docs)
                summary["databases"][db_name]["collections"][coll_name] = doc_count
                summary["total_documents"] += doc_count

                coll_file = os.path.join(db_path, f"{coll_name}.json")
                with open(coll_file, "w") as f:
                    json.dump(docs, f, default=json_util.default, indent=2)

                logger.info(f"✓ Backed up {db_name}.{coll_name}: {doc_count} documents")

                indexes = list(collection.list_indexes())
                idx_file = os.path.join(db_path, f"{coll_name}.indexes.json")
                with open(idx_file, "w") as f:
                    json.dump(indexes, f, default=json_util.default, indent=2)

        logger.info(f"\n✓ Backup completed: {backup_path}")
        logger.info(f"  Total documents: {summary['total_documents']}")

        client.close()
        return summary
    except ServerSelectionTimeoutError as sste:
        logger.error(f"Failed to connect to mongo server: '{uri}' because: {sste}")
        return {}
    except Exception as e:
        logger.error(f"Failed to ")
        return {}


@router.get("/mongo")
async def backup_mongo(name: str, port: int, request: Request):
    this_name = (
        f"mongo-{name}-{port}-{int(datetime.now(tz=timezone.utc).timestamp() * 1000)}"
    )
    output_dir = os.path.join(OUTPUT_DIR, this_name)
    backup_summary = mongodb_backup(
        uri=f"mongodb://localhost:{port}",
        output_dir=output_dir,
    )
    if backup_summary == {}:
        raise HTTPException(
            status_code=404, detail=f"No mongo instance found in port: '{port}'"
        )

    output_filename = os.path.join(OUTPUT_DIR, f"{this_name}.tar.gz")
    create_tarball(output_filename=output_filename, source_dir=output_dir)

    shutil.rmtree(output_dir)

    return {
        "backup_summary": backup_summary,
        "backup_url": os.path.join(
            request.base_url._url, os.path.join(STATIC_DIR, f"{this_name}.tar.gz")
        ),
    }


@router.get("/directory")
async def backup_dir(name: str, remote_path: str, request: Request):
    if not os.path.exists(remote_path):
        raise HTTPException(status_code=404, detail=f"'{remote_path}' does not exist!")

    this_name = (
        f"directory-{name}-{int(datetime.now(tz=timezone.utc).timestamp() * 1000)}"
    )
    output_dir = os.path.join(OUTPUT_DIR, this_name)

    if os.path.isdir(remote_path):
        logger.info(f"'{remote_path}' is a directory!")
        shutil.copytree(remote_path, output_dir)
    else:
        logger.info(f"'{remote_path}' is a file!")
        os.makedirs(output_dir, exist_ok=True)
        shutil.copy(remote_path, output_dir)

    logger.info(f"'{remote_path}' successfully copied!")

    output_filename = os.path.join(OUTPUT_DIR, f"{this_name}.tar.gz")
    create_tarball(output_filename=output_filename, source_dir=output_dir)

    logger.info(f"'{remote_path}' successfully tarballed!")

    shutil.rmtree(output_dir)

    logger.info(f"'{remote_path}' copied directory successfully cleaned!")

    return {
        "backup_url": os.path.join(
            request.base_url._url, os.path.join(STATIC_DIR, f"{this_name}.tar.gz")
        )
    }


@router.get("/delete")
async def delete_backup(tarball_name: str):
    backup_path = os.path.join(STATIC_DIR, tarball_name)

    if not os.path.exists(backup_dir):
        raise HTTPException(status_code=404, detail=f"'{backup_path}' does not exist!")

    os.remove(backup_path)

    return {"status": "success"}
