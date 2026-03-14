# Myrient-Search
This is a hopefully complete collection of all the links for every file that is currently available in Myrient: 2,782,560 files across 65,965 folders.

The data was obtained by using [RaimuV's myrient_scraper](https://github.com/RaimuV/myrient_scrape) and it is collected on the file *Myrient_links.json*.

In order to easily search the database, I also include the file *search_ui.py* which allows you to use search filters to find any file or folder:

    - Use quotes for exact phrase: "game iso"
    - Use AND/OR for logic: game AND iso OR rom
    - Use -word to exclude: game -demo
    - Filter by extension: ext=iso
    - Filter by size: size>500MB, size<2GB

 ## Usage:

  Simply make sure that you have both files on the same folder, run the file *search_ui.py* and open http://127.0.0.1:5000 to start browsing:

```
python search_ui.py
```
