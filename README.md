# IB_Flex
Assorted python scripts for downloading Interactive Brokers (IB) flex query, then saving and analyzing them.


The goal of this project is to store interactive broker account history in a sqlite database and analyse them using SQL/Python, perhaps with help of panda.

Some of the analysis in mind:

- Consider cost of funding, tax and dividend for single stock performance - hard to do with IB statements.  
- Tallying futures PnL over multiple rolling period.  
- Account Equity graph/drawdown analysis/ratios  

Prerequisite:
-------------
Python 3.6  
(Optional) SQLite DB browswer https://sqlitebrowser.org/  

Disclaimer:
-----------
**This is alpha software and just started developing, it just "worked" for me without any serious testing and I am not an experineced developer, so raising issues you found is welcome.**

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.**

Usage:
------
**xml_downloader.py**  
Call download_xml with token and report number, filename is optional.  
The resulting xml file will be saved in the same folder as the script.    
download_xml(token, report_number, filename='data.xml')    

Flex query report number is generated when you create a flex query.  
https://www.interactivebrokers.com.hk/en/software/am/am/reports/activityflexqueries.htm

Please refer to the link below on how to get the token
https://www.interactivebrokers.com.hk/en/software/am/am/reports/flex_web_service_version_3.htm  

example:
```
import xml_downloader
xml_downloader.download_xml('123456789012345', '123456', 'test.xml')
```
