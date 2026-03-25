# Myrient-Search
This is a hopefully complete collection of all the links for every file that is currently available in [Myrient](https://myrient.erista.me/): 2,782,560 files across 65,965 folders. **[Last updated on March 13, 2026]**

## Usage:

The data was obtained by using [RaimuV's myrient_scraper](https://github.com/RaimuV/myrient_scraper) and it is collected on the file *myrient_links.json*.

Simply make sure that you have both files on the same folder, run the file *search_ui.py* and open http://127.0.0.1:5000 to start browsing:

```
python search_ui.py
```

In order to easily search the database to find any file or folder you can use the following search features:

```
- Use quotes for exact phrase: "game iso"
- Use AND/OR for logic: game AND iso OR rom
- Use -word to exclude: game -demo
- Filter by extension: ext=iso
```

### Requirements

The search UI uses Flask so the corresponding library needs to be installed before running the script:
```
pip install flask
```

## A Final Note

Unfortunately, the team behind Myrient has announced that the website will close on March 31, 2026 and because the site's search system is limited to one folder at a time, this repository aims to preserve and index of the files and provide a convenient way to browse them globally.
 
For years Myrient has been one of the most valuable resources for video game preservation, providing thousands of users with reliable and convenient access to archived content, completely free. Please consider making a donation through [their official website](https://myrient.erista.me/donate/).
