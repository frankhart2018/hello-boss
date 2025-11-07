from fastapi import APIRouter
from pymongo import MongoClient
from datetime import datetime
import os
import json
from bson import json_util
import logging
import shutil

from ..utils.environment import OUTPUT_DIR
from ..utils.compress import create_tarball


router = APIRouter()

logger = logging.getLogger(__name__)


IGNORE_COLLECTIONS = ["admin", "local", "config"]


def mongodb_backup(uri: str, output_dir: str):
    client = MongoClient(uri)
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


@router.get("/mongo")
async def backup_mongo(port: int):
    this_name = f"mongo-{port}"
    output_dir = os.path.join(OUTPUT_DIR, this_name)
    backup_summary = mongodb_backup(
        uri=f"mongodb://localhost:{port}",
        output_dir=output_dir,
    )

    output_filename = os.path.join(OUTPUT_DIR, f"{this_name}.tar.gz")
    create_tarball(output_filename=output_filename, source_dir=output_dir)

    shutil.rmtree(output_dir)

    return {"backup_summary": backup_summary, "output_filename": output_filename}
