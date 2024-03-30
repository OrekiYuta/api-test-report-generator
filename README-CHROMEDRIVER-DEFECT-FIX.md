# Fix chromedriver-autoinstaller defect

- Chrome v115+
- chromedriver_autoinstaller == 0.6.2
- locate to source utils.py

## For Windows

### Point 1

```python
def get_matched_chromedriver_version(chrome_version, no_ssl=False):
    # Newer versions of chrome use the CfT publishing system
    if chrome_version >= "115":
        version_url = "googlechromelabs.github.io/chrome-for-testing/known-good-versions.json"
        version_url = "http://" + version_url if no_ssl else "https://" + version_url
        good_version_list = json.load(urllib.request.urlopen(version_url))
        compare_version = chrome_version.rsplit('.', 1)[0]
        for good_version in good_version_list["versions"]:
            # if good_version["version"] == chrome_version:
            #     return chrome_version
            if good_version["version"].startswith(compare_version):
                return good_version["version"]
    # check old versions of chrome using the old system
    else:
        version_url = "chromedriver.storage.googleapis.com"
        version_url = "http://" + version_url if no_ssl else "https://" + version_url
        doc = urllib.request.urlopen(version_url).read()
        root = elemTree.fromstring(doc)
        for k in root.iter("{http://doc.s3.amazonaws.com/2006-03-01}Key"):
            if k.text.find(get_major_version(chrome_version) + ".") == 0:
                return k.text.split("/")[0]
    return
```

### Point 2

```python
def get_chrome_version():
    if platform == "linux":
    elif platform == "mac":
    elif platform == "win":
        # check both of Program Files and Program Files (x86).
        # if the version isn't found on both of them, version is an empty string.

        # dirs = [f.name for f in os.scandir("C:\\Program Files\\Google\\Chrome\\Application") if f.is_dir() and re.match("^[0-9.]+$", f.name)]
        # if dirs:
        #     version = max(dirs)
        # else:
        #     dirs = [f.name for f in os.scandir("C:\\Program Files (x86)\\Google\\Chrome\\Application") if f.is_dir() and re.match("^[0-9.]+$", f.name)]
        #     version = max(dirs) if dirs else ''

        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application"
        if not os.path.exists(chrome_path):
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application"

        try:
            dirs = [f.name for f in os.scandir(chrome_path) if f.is_dir() and re.match("^[0-9.]+$", f.name)]
            version = max(dirs) if dirs else ''
        except FileNotFoundError:
            version = ''

    else:
        return
    return version
```
