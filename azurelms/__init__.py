import asyncio
import base64
import functools
import logging
import os
import time

import aiohttp
import azure.functions as func


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
async def main(mytimer: func.TimerRequest) -> None:
    logging.info("******* Starting main function *******")
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
        async with session.put(
            url=f"https://graph.microsoft.com/v1.0/drives/{os.environ['DRIVE_ID']}/root:/GoFex%20Reporting/{myblob.name.split('/')[-1]}:/content",
            headers=graph_api_headers,
            data=myblob.read(),
        ) as resp:
            status = resp.status
            logging.info(f"Response status code: {status}")
            logging.info(f"Response body: {await resp.json()}")

        async with session.post(
            url=os.environ["LOGICAPP_URI"],
            json={
                "Name": f"{myblob.name.split('/')[-1]}",
                "BlobSize": f"{myblob.length} bytes",
                "BlobUri": f"{myblob.uri}",
                "Status": f"{status}",
            },
        ) as resp:
            logging.info(
                f"******* Finishing main function with status {resp.status} *******"
            )
