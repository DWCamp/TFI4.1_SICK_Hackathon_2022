"""
Ah, the dreaded "utils" junk drawer

Author: D. William Campman
Date: 2022-10-05
"""

import aiohttp


async def async_get(url, headers=None, params=None):
    """
    Makes an asynchronous GET request

    Parameters
    -------------
    url : str
        The url to request from
    params : Optional - dict{str:str}
        Parameters passed in the request (Default: empty dict)
    headers : dict{str:str}
        Headers passed in the request (Default: empty dict)
    content_type : Optional - String

    Returns
    -------------
    The response object
    """
    # Create parameter and header dictionary if none passed
    headers = {} if headers is None else headers
    params = {} if params is None else params

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params) as resp:
            return resp


async def async_get_json(url, headers=None, params=None):
    """
    Requests JSON data using a GET request

    Parameters
    -------------
    url : str
        The url to request from
    params : Optional - dict{str:str}
        Parameters passed in the request (Default: empty dict)
    headers : dict{str:str}
        Headers passed in the request (Default: empty dict)

    Returns
    -------------
    If the request is valid, a tuple
    [0] - json dictionary
    [1] - resp.status

    If the request fails, a tuple
    [0] - None
    [0] - resp.status
    """
    # Create parameter and header dictionary if none passed
    headers = {} if headers is None else headers
    params = {} if params is None else params

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                json = await resp.json()
                return json, 200
            return None, resp.status


async def async_post(url, params=None, headers=None, json=None):
    """
    Requests JSON data using a POST request

    Parameters
    -------------
    url : str
        The url to request from
    params : Optional - dict{str:str}
        Parameters passed in the request.
    headers : dict{str:str}
        Headers passed in the request
    json : Optional - dict{str:str}
        The JSON dictionary to be posted with the API

    Returns
    -------------
    If the request is valid, a tuple
    [0] - json dictionary
    [1] - resp.status

    If the request fails, a tuple
    [0] - None
    [0] - resp.status
    """
    # Create parameter and header dictionary if none passed
    headers = {} if headers is None else headers
    params = {} if params is None else params

    # Create json dictionary if none passed
    if json is None:
        json = {}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, params=params, json=json) as resp:
            json = await resp.json() if resp.status == 200 else None
            return json, resp.status
