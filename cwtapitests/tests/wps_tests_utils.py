"""
===============
WPS Tests Utils
===============

Functions:

 * :func:`xml_children_as_dict` - create dictionary from xml element children.
 * :func:`xml_attrib_nsmap` - replace nsmap values with their key.
 * :func:`parse_execute_response` - parse wps execute response.
 * :func:`wps_response` - get xml document response from a WPS.
 * :func:`get_wps_xlink` - read a document from an url.
 * :func:`config_is_available` - skip tests when config is unavailable.

"""

import unittest
from lxml import etree

import requests
from owslib.wps import WebProcessingService, WPSReader, WPSExecution


def xml_children_as_dict(element):
    """Create dictionary from xml element children.

    Parameters
    ----------
    element : lxml.etree._Element

    Returns
    -------
    out : dict

    Notes
    -----
    An additional replacement of the nsmap values with their key is done
    on the tag of each child.

    """

    d = {}
    for child in element:
        child_tag = child.tag
        for key, nsvalue in child.nsmap.items():
            child_tag = child_tag.replace('{' + nsvalue + '}', key + ':')
        if child_tag in d:
            d[child_tag].append(child)
        else:
            d[child_tag] = [child]
    return d


def xml_attrib_nsmap(element):
    """Replace nsmap values with their key in element attributes.

    Parameters
    ----------
    element : lxml.etree._Element

    Returns
    -------
    out : dict
        element.attrib with the replaced nsmap.

    """

    d = {}
    for key, value in element.attrib.items():
        new_key = key
        for nskey, nsvalue in element.nsmap.items():
            new_key = new_key.replace('{' + nsvalue + '}', nskey + ':')
        d[new_key] = value
    return d


def parse_execute_response(html_response):
    """Parse WPS execute response.

    Parameters
    ----------
    html_response : string
        xml document from an execute WPS request.

    Returns
    -------
    out : dict
        'identifier' : wps:Process -> ows:Identifier
        'status' : wps:Status -> {tag of the status, without nsmap}
        'ouputs' : wps:ProcessOutputs -> wps:Output ->
                   {ows:Identifier : wps:Data}

    """

    # XML structure:
    # wps:ExecuteResponse
    #     wps:Process
    #         ows:Identifier (text)
    #         ows:Title (text)
    #     wps:Status
    #         creationTime (attrib)
    #         wps:ProcessSucceeded (xor, text)
    #         wps:ProcessFailed (xor, text)
    #         wps:ProcessAccepted (xor, text)
    #         wps:ProcessStarted (xor, text)
    #             percentCompleted (attrib)
    #     wps:ProcessOutputs
    #         wps:Output (list)
    #             ows:Identifier (text)
    #             ows:Title (text)
    #             wps:Data (xor)
    #                 wps:LiteralData (xor)
    #                 [...]
    #             wps:Reference (xor)
    #                 xlink:href (attrib)
    #                 mimeType (attrib)
    d = {'outputs': {}}
    execute_response_element = etree.fromstring(html_response)
    execute_response_attrib = xml_attrib_nsmap(execute_response_element)
    if 'statusLocation' in execute_response_attrib:
        d['statusLocation'] = execute_response_attrib['statusLocation']
    execute_response = xml_children_as_dict(execute_response_element)

    process = xml_children_as_dict(execute_response['wps:Process'][0])
    d['identifier'] = process['ows:Identifier'][0].text

    status_element = execute_response['wps:Status'][0]
    status_attrib = xml_attrib_nsmap(status_element)
    status = xml_children_as_dict(status_element)
    d['creationTime'] = status_attrib['creationTime']
    if 'wps:ProcessSucceeded' in status:
        d['status'] = 'ProcessSucceeded'
    elif 'wps:ProcessFailed' in status:
        d['status'] = 'ProcessFailed'
        return d
    elif 'wps:ProcessAccepted' in status:
        d['status'] = 'ProcessAccepted'
        return d
    elif 'wps:ProcessStarted' in status:
        process_started_element = status['wps:ProcessStarted'][0]
        process_started_attrib = xml_attrib_nsmap(process_started_element)
        d['status'] = 'ProcessStarted'
        d['percentCompleted'] = \
            float(process_started_attrib['percentCompleted'])
        return d
    else:
        raise NotImplementedError()

    process_outputs = xml_children_as_dict(
        execute_response['wps:ProcessOutputs'][0])
    for output_element in process_outputs['wps:Output']:
        output1 = xml_children_as_dict(output_element)
        identifier = output1['ows:Identifier'][0].text
        if 'wps:Data' in output1:
            data1 = xml_children_as_dict(output1['wps:Data'][0])
            if 'wps:LiteralData' in data1:
                d['outputs'][identifier] = data1['wps:LiteralData'][0].text
            else:
                raise NotImplementedError()
        elif 'wps:Reference' in output1:
            reference_element = output1['wps:Reference'][0]
            reference_attrib = xml_attrib_nsmap(reference_element)
            d['outputs'][identifier] = reference_attrib['xlink:href']
        else:
            raise NotImplementedError()
    return d


def get_capabilities(wps_host=None, wps_client=None, version='1.0.0'):
    """WPS GetCapabilities response.

    Parameters
    ----------
    wps_host : string
    wps_client : pywps.tests.WpsClient
    version : string

    Returns
    -------
    out : list of ?

    """

    if wps_host:
        return WebProcessingService(wps_host, version)
    else:
        response = wps_client.get(
            '?service=WPS&request=GetCapabilities&version={0}'.format(version))
        wps_reader = WPSReader()
        element = wps_reader.readFromString(response.get_data())
        wps = WebProcessingService(None, version, skip_caps=True)
        wps._parseCapabilitiesMetadata(element)
        return wps


def describe_process(identifier, wps_host=None, wps_client=None,
                     version='1.0.0'):
    """WPS Describe Process response.

    Parameters
    ----------
    identifer : string
    wps_host : string
    wps_client : pywps.tests.WpsClient
    version : string

    Returns
    -------
    out : list of ?

    """

    if wps_host:
        wps = WebProcessingService(wps_host, version)
        return wps.describeprocess(identifier)
    else:
        response = wps_client.get(
            ('?service=WPS&request=DescribeProcess&version={0}&'
             'identifier={1}').format(version, identifier))
        wps_reader = WPSReader()
        element = wps_reader.readFromString(response.get_data())
        wps = WebProcessingService(None, version, skip_caps=True)
        return wps._parseProcessMetadata(element)


def execute(identifier, inputs=[], wps_host=None, wps_client=None,
            version='1.0.0'):
    """WPS execute response.

    Parameters
    ----------
    identifer : string
    inputs : list of tuples
    wps_host : string
    wps_client : pywps.tests.WpsClient
    version : string

    Returns
    -------
    out : list of ?

    """

    if wps_host:
        wps = WebProcessingService(wps_host, version)
        return wps.execute(identifier, inputs=inputs)
    else:
        y = ''
        for data_input in inputs:
            y += '{0}={1};'.format(data_input[0], data_input[1])
        y = y[:-1]
        response = wps_client.get(
            ('?service=WPS&request=execute&version={0}&'
             'identifier={1}&DataInputs={2}').format(version, identifier, y))
        wps_reader = WPSReader()
        element = wps_reader.readFromString(response.get_data())
        execution = WPSExecution()
        execution._parseExecuteResponse(element)
        return execution


def get_wps_xlink(xlink, output_file=None):
    if output_file:
        r = requests.get(xlink, stream=True)
        with open(output_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return output_file
    else:
        r = requests.get(xlink)
        return r.text


def config_is_available(config_section, config_names, config_read,
                        set_wps_host=False):
    """Check if a config section & parameters are available for tests.

    Parameters
    ----------
    config_section : string
        section of a cfg file.
    config_names : list of string
        name of parameters to check.
    config_read : result from read method of ConfigParser.RawConfigParser
    set_wps_host : bool
        whether to set a default wps_host in the output config dictionary,
        if there is already one, it is not overwritten.

    Returns
    -------

    out : dict
        dictionary of parameter:value for all parameters of the given section

    """

    if not hasattr(config_names, '__iter__'):
        config_names = [config_names]
    if config_section not in config_read.sections():
        raise unittest.SkipTest(
            "{0} section not defined in config.".format(config_section))
    section = config_read.items(config_section)
    section_d = {}
    for item in section:
        section_d[item[0]] = item[1]
    for config_name in config_names:
        if (config_name not in section_d) or (not section_d[config_name]):
            raise unittest.SkipTest(
                "{0} not defined in config.".format(config_name))

    if set_wps_host:
        if 'wps_host' in section_d:
            # wps_host might be set, but empty. If that's the case, set to None
            if not section_d['wps_host']:
                section_d['wps_host'] = None
        else:
            section_d['wps_host'] = None

    return section_d
