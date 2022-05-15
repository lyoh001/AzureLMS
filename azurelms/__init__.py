import asyncio
import base64
import functools
import io
import logging
import os
import time

import aiohttp
import azure.functions as func
import pandas as pd
from azure.storage.blob import BlobClient


def timer(func):
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            logging.info(
                f"total execution time for async {func.__name__}: {time.time() - start_time}"
            )
            if result:
                return result

        return wrapper
    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            logging.info(
                f"total execution time for sync {func.__name__}: {time.time() - start_time}"
            )
            if result:
                return result

        return wrapper


def get_api_headers_decorator(func):
    @functools.wraps(func)
    async def wrapper(session, *args, **kwargs):
        return {
            "Authorization": f"Basic {base64.b64encode(bytes(os.environ[args[0]], 'utf-8')).decode('utf-8')}"
            if "PAT" in args[0]
            else f"Bearer {os.environ[args[0]] if 'EA' in args[0] else await func(session, *args, **kwargs)}",
            "Content-Type": "application/json-patch+json"
            if "PAT" in args[0]
            else "application/json",
        }

    return wrapper


@get_api_headers_decorator
async def get_api_headers(session, *args, **kwargs):
    oauth2_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    oauth2_body = {
        "client_id": os.environ[args[0]],
        "client_secret": os.environ[args[1]],
        "grant_type": "client_credentials",
        "scope" if "GRAPH" in args[0] else "resource": args[2],
    }
    async with session.post(
        url=args[3], headers=oauth2_headers, data=oauth2_body
    ) as resp:
        return (await resp.json())["access_token"]


@timer
async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("******* Starting main function *******")
    upn = os.environ["UPN"]
    async with aiohttp.ClientSession() as session:
        graph_api_headers = next(
            iter(
                await asyncio.gather(
                    *(
                        get_api_headers(session, *param)
                        for param in [
                            [
                                "GRAPH_CLIENT_ID",
                                "GRAPH_CLIENT_SECRET",
                                "https://graph.microsoft.com/.default",
                                f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}/oauth2/v2.0/token",
                            ]
                        ]
                    )
                )
            )
        )
        async with session.get(
            f"https://graph.microsoft.com/v1.0/users/{upn}/messages",
            headers=graph_api_headers,
        ) as resp:
            status = resp.status
            logging.info(f"Response status code: {status}")
            df = pd.DataFrame((await resp.json())["value"])
            id = (
                df[
                    df.apply(
                        lambda row: "LMS DATA" in row["subject"]
                        and row["hasAttachments"] == True,
                        axis=1,
                    )
                ]
                .sort_values(by="receivedDateTime", ascending=False)
                .iloc[0]["id"]
            )
        async with session.get(
            f"https://graph.microsoft.com/v1.0/users/{upn}/messages/{id}/attachments",
            headers=graph_api_headers,
        ) as resp:
            attachments = (await resp.json())["value"]
            content = base64.b64decode(
                next(
                    iter(
                        f["contentBytes"]
                        for f in attachments
                        if ".csv" in f["name"].lower()
                    )
                )
            ).decode("utf-8")
            toread = io.StringIO()
            toread.write(content)
            toread.seek(0)
            df = pd.read_csv(toread)

            blob_client = BlobClient.from_connection_string(
                conn_str=os.environ["STORAGE_ACCT_APP_SETTING"],
                container_name="azurelmsstrg",
                blob_name="LMS DATA 1.csv",
            )
            try:
                blob_client.upload_blob(df.to_csv(index=False), overwrite=True)
                logging.info("******* Finishing main function with status 200 *******")
                return func.HttpResponse("Success", status_code=200)

            except Exception as e:
                logging.info(
                    f"******* Finishing main function with status 500 *******\n{e}"
                )
                return func.HttpResponse(f"Error: {e}", status_code=500)
