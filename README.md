## Depot Tracker

============

### A. Import from Consors broker

1. Log-in into Consors broker and export your current depot as CSV file(s).
2. Place CSV file(s) into directory dir/
3. Import using
```
    python3 import_from_consors_csv.py --plot True --label "7. Sep. 2021" /tmp/consors_csv/07092021/
```

### B. Import WKN to ISIN mapping
In order to get the live price of your stocks you need the International Securities Identification Number (ISIN) of each stock 

1. Add for each stock you might have in your depot a WKN to ISIN mapping
```
    nano tradegate/wkn_isin.txt
```
2. Import the WKN-2-ISIN mapping
```
    python3 import_wkn_to_isin.py
```

### C. Import additional assets like gold, crypto
As an example you might have other assets like gold or crypto which you can import here:
```
    python3 import_vault.py
```


### D. Watch the value of your depot in live or offline
```
    python3 live_depot.py
```
You can also see the depot value since last update: 
```
    python3 offline_depot.py
```