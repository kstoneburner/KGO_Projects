import time, datetime, requests,random, os, hashlib

from pathlib import Path

import pandas as pd

from scrape_functions import *

#//*** install xlsxwriter for pandas
#pip install xlsxwriter



#//*********************************************************
#//*** Build the tgt_date from the slected Quarter and Year
#//*********************************************************
tgt_year = 2023
quarter = "Q2"


#//*** URLS and Category Labels
url_items = [
    {
        "url" : "https://abc7news.com/tag/climate-change/",
        "cat" : "Climate"
    },
    {
        "url" : "https://abc7news.com/tag/environment/",
        "cat" : "Environment"
    },
 
    {
        "url" : "https://abc7news.com/tag/economy/",
        "cat" : "Economy"
    },
    {
        "url" : "https://abc7news.com/tag/jobs/",
        "cat" : "Jobs"
    },    
    {
        "url" : "https://abc7news.com/tag/safety/",
        "cat" : "Safety"
    },
    {
        "url" : "https://abc7news.com/tag/health/",
        "cat" : "Health"
    },
    {
        "url" : "https://abc7news.com/education/",
        "cat" : "Education"
    },
    {
        "url" : "https://abc7news.com/tag/race-and-culture/",
        "cat" : "Race"
    },
    {
        "url" : "https://abc7news.com/tag/discrimination/",
        "cat" : "Discrimination"
    },
    {
        "url" : "https://abc7news.com/tag/civil-rights/",
        "cat" : "Civil Rights"
    },
    {
        "url" : "https://abc7news.com/tag/building-a-better-bay-area/",
        "cat" : "BABBA"
    },
    {
        "url" : "https://abc7news.com/7onyourside/",
        "cat" : "7OYS"
    },
    {
        "url" : "https://abc7news.com/tag/covid-19/",
        "cat" : "COVID"
    },

    {
        "url" : "https://abc7news.com/iteam/",
        "cat" : "I-TEAM"
    },
    

    
]


#//**********************************************************
#//**** Initialization
#//**********************************************************

#//*** Fresh DataFrame
df = pd.DataFrame()

#//*** Get Filename for dataframe Cache
cache_filepath =  f"{tgt_year}_{quarter}_scripts.dat"
current_dir = Path(os.getcwd()).absolute()
cache_filepath = current_dir.joinpath(cache_filepath)

#//*** Build Target Date BAsed on Quarter
if quarter == "Q1":
    tgt_date = f"{tgt_year}-01-01"
elif quarter == "Q2": 
    tgt_date = f"{tgt_year}-04-01"
elif quarter == "Q3": 
    tgt_date = f"{tgt_year}-07-01"
elif quarter == "Q4": 
    tgt_date = f"{tgt_year}-10-01"

#//*** Target Date will be in epoch Time
tgt_date = int(datetime.datetime.strptime(tgt_date, "%Y-%m-%d").timestamp())

print(tgt_date)

#//**** Dummy Values for element Testing
#cat = "I-TEAM"
#url = "https://abc7news.com/iteam/"
#print("getting URLS from: " + url)
#urls = get_all_urls_in_page(url,tgt_date,False)
#story = get_story("https://abc7news.com/alameda-county-district-attorney-pamela-price-judge-mark-mccannon-video-delonzo-logwood/13100696/")
#print("Title: " + story['title'])
#print("Description: " + story['description'])
#print("url: " + story['url'])
#print("Epoch: "+ str(story['epoch']) + " : " + story['date'])
#print(str(tgt_date) + ":" + str(story['epoch']) + ":" + str(tgt_date > story['epoch'])) 
#print("Text: "+ story['body'])
#urls = ['https://abc7news.com/oakland-ransomware-hacked-data-leaked-fbi-dark-web/13225220/', 'https://abc7news.com/gardener-speaks-out-san-rafael-police-use-of-force-beer-beating-mateo/13215522/', 'https://abc7news.com/san-mateo-county-board-of-supervisors-immigration-ordinance-immigrant-crime-bay-area-asylum-seekers/13213284/', 'https://abc7news.com/ca-affordable-housing-oakland-choice-voucher-hud-department-of/13212762/', 'https://abc7news.com/pge-undergrounding-powerlines-wildfire-risk-oakland-hills/13181565/', 'https://abc7news.com/antioch-police-cellphone-video-excessive-force-federal-civil-rights-lawsuit/13187553/', 'https://abc7news.com/san-mateo-county-immigrant-crime-bay-area-asylum-seekers-convicted-immigrants-deportation/13182640/', 'https://abc7news.com/san-mateo-county-sanctuary-co-asylum-seekers-convicted-immigrants-deportation/13156977/', 'https://abc7news.com/bob-lee-death-timeline-stabbing-nima-momeni-arrest/13128421/', 'https://abc7news.com/restorative-justice-bay-area-peacemaker-fellowship-community-works/13114760/', 'https://abc7news.com/oakland-ransomware-social-security-hack-data-leak-info-stolen/13120130/', 'https://abc7news.com/alameda-county-district-attorney-pamela-price-judge-mark-mccannon-video-delonzo-logwood/13100696/', 'https://abc7news.com/bob-lee-killed-surveillance-image-san-francisco-stabbing/13096712/', 'https://abc7news.com/bob-lee-dead-cash-app-mobilecoin/13094980/', 'https://abc7news.com/bob-lee-dead-cash-app-mobilecoin/13087740/', 'https://abc7news.com/trump-arraignment-supporters-protesters/13086871/', 'https://abc7news.com/internet-archive-lawsuit-sf-digital-library-online-free/13080303/', 'https://abc7news.com/alameda-county-district-attorney-pamela-price-oakland-arena-closed-door-meeting/13060331/', 'https://abc7news.com/california-flavored-tobacco-ban-e-cigarette-vaping-laws-nicotine/13044276/', 'https://abc7news.com/california-flavored-tobacco-ban-black-market-atf-prop-31/13059161/', 'https://abc7news.com/california-flavored-tobacco-ban-e-cigarette-vaping-laws-sunnyvale/13051007/', 'https://abc7news.com/alameda-county-da-pamela-price-email-crimes-against-asian-americans-jasper-wu-oakland/13045085/', 'https://abc7news.com/california-flavored-tobacco-ban-e-cigarette-vaping-laws-teens/13042455/', 'https://abc7news.com/pamela-price-alameda-county-district-attorney-charly-weissenbach-policies/13030644/', 'https://abc7news.com/oakland-ransomware-city-of-hacked-stonewalling-cyberattack/13030898/', 'https://abc7news.com/oakland-ransomware-city-of-hacking-cyberattack-mayor-sheng-thao/12983940/', 'https://abc7news.com/oakland-ransomware-attack-dark-web-play-randomware/12965273/', 'https://abc7news.com/rome-police-stabbing-appeal-italian-officer-murder-finnegan-elder-gabriel-natale-hjorth/12958716/', 'https://abc7news.com/batmobile-raid-independent-investigation-confidential-report-san-mateo-sheriff/12954540/', 'https://abc7news.com/santa-rosa-diocese-bankruptcy-catholic-church-child-sex-abuse-lawsuits/12950488/', 'https://abc7news.com/play-ransomware-oakland-stolen-data-attack/12931292/', 'https://abc7news.com/war-in-ukraine-russia-united-nations-news/12930819/', 'https://abc7news.com/oakland-ransomware-data-leak-hackers-employee-information/12923030/', 'https://abc7news.com/sf-mayor-london-breed-brother-napoleon-brown-sentencing-hearing-manslaughter-conviction-murder-2020/12922147/', 'https://abc7news.com/belvedere-coyotes-usda-snipers-marin-county-coyote-island/12911980/', 'https://abc7news.com/oakland-sex-trafficking-workers-pimps-e-15th-st-barricades/12911104/', 'https://abc7news.com/ca-loitering-law-sex-trafficking-sb-357-workers/12910562/', 'https://abc7news.com/san-rafael-police-use-of-force-gardener-files-claim-officer-daisy-mazariegos-brandon-nail/12868510/', 'https://abc7news.com/san-francisco-mission-barricades-sex-workers-capp-street-barriers-ca-state-statute-violation/12874237/', 'https://abc7news.com/san-francisco-red-light-district-sex-workers-supervisor-hillary-ronen-nevada-prostitution/12862492/', 'https://abc7news.com/san-francisco-red-light-district-sf-mission-street-barriers-firefighter-union-tweet-sex-workers/12856857/', 'https://abc7news.com/oakland-sex-trafficking-church-helping-workers-victory-outreach-st-anthonys-school/12850611/', 'https://abc7news.com/sf-muni-bus-egging-asian-hate-attack-san-francisco-anti-crime/12834079/', 'https://abc7news.com/oakland-sound-wall-high-street-off-ramp-i-team-helps-residents-cal-trans-repairs/12827800/', 'https://abc7news.com/shooting-michigan-state-anthony-dwayne-mcrae-university-victims/12824658/', 'https://abc7news.com/sf-affordable-housing-broken-elevator-homerise-elderly-residents-disabled/12821442/', 'https://abc7news.com/california-red-light-district-legalizing-prostitution-sf-supervisor-hillary-ronen-sex-workers/12816587/', 'https://abc7news.com/san-francisco-red-light-district-street-barries-sex-workers-prostitution/12811362/', 'https://abc7news.com/california-wildfires-pge-fire-victim-settlement-relief-for-wildfire-victims/12794424/', 'https://abc7news.com/oakland-human-trafficking-prostitution-st-anthonys-catholic-school-scott-weiner/12793766/', 'https://abc7news.com/rabies-shot-hospital-bill-vacaville-ca-couple-northbay-healthcare-vacavalley/12788545/', 'https://abc7news.com/oakland-human-trafficking-prostitution-st-anthonys-catholic-school-young-girls/12768428/', 'https://abc7news.com/human-trafficking-prostitution-oakland-catholic-school-st-anthonys/12764548/', 'https://abc7news.com/woman-beheaded-san-carlos-rafa-solano-interview-mateo-county-jail-karina-castro/12763168/', 'https://abc7news.com/jellys-place-san-pablo-bay-area-no-kill-animal-shelter-caltrans-land-owner-rescue/12751605/', 'https://abc7news.com/san-rafael-police-use-of-force-gardener-files-claim-takedown-body-cam-video/12742823/', 'https://abc7news.com/half-moon-bay-shooting-chunli-zhao-execution-style-mass-shooter/12736302/', 'https://abc7news.com/half-moon-bay-shooting-mass-suspect-chunli-zhao-charged-san-mateo-county-da/12735739/', 'https://abc7news.com/mass-shootings-half-moon-bay-shooting-monterey-park-gun-violence/12732195/', 'https://abc7news.com/half-moon-bay-mass-shooting-suspect-chunli-zhao-history-workplace-violence-hmb/12731878/', 'https://abc7news.com/oakland-police-chief-leronne-armstrong-administrative-leave-misconduct-investigation/12720512/', 'https://abc7news.com/tiffany-li-keith-green-kaveh-bayat-olivier-adella/12719821/', 'https://abc7news.com/opd-chief-leronne-armstrong-oakland-police-on-administrative-leave-news-mayor-sheng-thao/12719720/', 'https://abc7news.com/opd-chief-leronne-armstrong-oakland-police-on-administrative-leave-news-mayor-sheng-thao/12720499/', 'https://abc7news.com/highway-92-sinkhole-san-mateo-closure-coast/12699490/', 'https://abc7news.com/ambulance-bill-er-trip-cost-medical-transport/12690317/', 'https://abc7news.com/tesla-sf-bay-bridge-crash-8-car-self-driving-video/12686428/', 'https://abc7news.com/emergency-department-statistics-room-capacity-california-ers-in-san-francisco-unhoused-population/12629461/', 'https://abc7news.com/boyes-hot-springs-sonoma-valley-real-estate-investment-wakeupsonoma/12607036/', 'https://abc7news.com/pge-employees-wildfire-season-reducing-workforce/12579571/', 'https://abc7news.com/glitter-bomb-package-mark-rober-youtube-video-sf-car-break-in/12594779/', 'https://abc7news.com/officer-shoots-neighbors-dog-novato-police-swat-leader-nick-frey-bay-area-use-of-force-video/12575363/']
#url_items = [ { "url" : "https://abc7news.com/iteam/", "cat" : "I-TEAM" }]



#//**** Download All The Stories
stories = download_all_stories(url_items,tgt_date)


print("Processing Stories")
#//**** Placeholder object to convert to DataFrame
s = {}

#//*** Get each script value as a list
for story in stories:

    for key,value in story.items():
        if key == 'error':
            continue
        if key not in s.keys():
            s[key] = []

        s[key].append(value)

#//*** build Urls field
#//*** Use the Story URL in case an url was skipped.
df['urls'] = s['url']
df['hash'] = pd.util.hash_pandas_object(df['urls'])

#//*** Convert Placeholder Object lists into DataFrame Columns
for key,value in s.items():
    df[key] = value

#//*** Everything is Gathered. Write df to disk
#//*** Write DF to file
pd.to_pickle(df,cache_filepath)

df = pd.read_pickle(cache_filepath)

print(df)

df.drop_duplicates(subset="url")
df.drop_duplicates(subset="description")

#//*** Write to excel file
output_filename = f"{tgt_year}_{quarter}_Collected_Stories.xlsx"
print(output_filename)

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')

#//*** Build Sheet and Data from From each url_item element
for url_item in url_items:
    sheet = url_item['cat']
    
    tdf = df[df['cat'] == sheet].copy().sort_values("date",ascending=False)
    
    tdf = tdf[['url','date','title','body']]
    
    tdf.to_excel(writer,sheet_name=sheet)
    

workbook = writer.book


cell_format = workbook.add_format()


for url_item in url_items:
    sheet = url_item['cat']
    writer.sheets[sheet].set_column(2,2, 10)      
    writer.sheets[sheet].set_column(4,4, 20) 
    
for url_item in url_items:
    sheet = url_item['cat']
    cell_format.set_font_name('Arial')
    cell_format.set_font_size(12)


     
    writer.sheets[sheet].set_column('A:F', None, cell_format)  
    
    
try:
    writer.close()    
except:
    print("Trouble Saving the Spreadsheet. It's Probably Open Somewhere. Close it and Retry")   

#//***

#print(urls)

'''









print(df)


df = pd.read_pickle(cache_filepath)

print(df)

df.drop_duplicates(subset="url")
df.drop_duplicates(subset="description")

print(df)
print(df.columns)
print(df['title'])
print(df['cat'])



#try:
#    df['time_date'] = df['epoch'].dt.date
#except:
#    pass
'''

