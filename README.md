# Hello Boss

On demand information fetching service meant to be run on servers to aggregate data. 

## Warning

Do not run it inside docker container, just run it as a normal process. Maybe use [pm2](https://pm2.keymetrics.io/).

## Dependencies

1. Install all python libraries in requirements.txt:

```bash
pip install -r requirements.txt
```

2. Install uvicorn to run the app:

```bash
pip install uvicorn
```

## Run

Got windows? Ever considered switching to macOS/Linux? No? Ok, goodbye, stop reading now.

Still here? I trust you now, continue reading.

```bash
bash run.sh
```

OR

```bash
chmod +x run.sh && ./run.sh
```