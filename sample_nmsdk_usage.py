from netapp_nmsdk import NaElement, NaServer # for NMSDK


def is_filer_7mode_get_ontap_ver(filer):
    """
    Returns ontap version for 7 mode filer.
    Uses NMSDK.
    Keyword arguments:
    filer -- A valid filer DNS name or IP address
    Returns:
      Error message "FAILED 7MODE" and reason if failed to get ontap version.
      ontap version number and "7MODE PASS" if success in getting ontap version
    """
    s = NaServer(filer, 1, 8)
    s.set_server_type("FILER")
    s.set_transport_type("HTTPS")
    s.set_port(443)
    s.set_style("LOGIN")
    s.set_admin_user("username", "password")
    s.set_timeout(10)  
    api = NaElement("system-get-ontapi-version")
    try:
        xo = s.invoke_elem(api)
    except:
        return(s, "FAILED 7MODE", "ConnectionResetError: [Errno 54] Connection reset by peer")
    if xo.results_status() == "failed":
        return(s, "FAILED 7MODE", xo.sprintf().strip())
    else:
        results_dict = xmltodict.parse(str(xo.sprintf()).strip())
        try:
            return (s, str(results_dict['results']['major-version']+"."+results_dict['results']['minor-version']), "7MODE PASS")
        except:
            return (s, "FAILED 7MODE", xo.sprintf().strip())     
        
def is_filer_cdot_get_ontap_ver(filer):
    """
    Returns ontap version for CDOT mode filer.
    Uses NMSDK.
    Keyword arguments:
    filer -- A valid filer DNS name or IP address
    Returns:
      Error message "FAILED CDOT" and reason if failed to get ontap version.
      ontap version number and "CDOT PASS" if success in getting ontap version.
    Iterates thru version numbers until correct version number is found and returns
    version number.
    """
    seeking_version = True
    version = 190
    while seeking_version == True and version > 110:
        s = NaServer(filer, 1, str(version))
        s.set_server_type("FILER")
        s.set_transport_type("HTTPS")
        s.set_port(443)
        s.set_style("LOGIN")
        s.set_admin_user("username", "password")
        s.set_timeout(10) 
        api = NaElement("system-get-ontapi-version")
        xo = s.invoke_elem(api)
        result = xo.sprintf().strip()
        if xo.results_status() == "failed":
            if "Authorization failed" in result or "Connection refused" in result or "Network is unreachable" in result or "or not known" in result:
                return(s, "FAILED CDOT", "Authorization failed" )
        if xo.results_status() == "failed":
            version = version - 10
        else:
            seeking_version = False
    results_dict = xmltodict.parse(str(result))
    try:
        return (s, str(results_dict['results']['major-version']+"."+results_dict['results']['minor-version']),"CDOT PASSED")
    except:
        return (s, "FAILED CDOT", str(result))

def get_filer_version(filer):
    """
    Used to get OnTap version of filer and type of filer:
    either cdot or 7mode.
    Makes 1 to 2 calls related functions to determine NMSDK level
    Returns filer Ontap version and type.
    Keyword arguments:
    filer -- STRING DNS Name or IP adddress of filer.
    Returns:
      OnTap version, and one of "7mode" or "cdot"
    """
    s, version, return_status = is_filer_cdot_get_ontap_ver(filer)
    if version == "FAILED CDOT":
        s, version, return_status = is_filer_7mode_get_ontap_ver(filer)
        if version == "FAILED 7MODE":
            return(s, str(return_status), "FAILED")
        else:
            return(s, str(version),"7mode")
    else:
        return(s, str(version), "cdot")
    
