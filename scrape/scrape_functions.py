from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By

import requests,re,json,datetime,time,random

def download_all_stories(url_items,tgt_date):
    
    out = []
    #//*** Loop through each url_item

    for url_item in url_items:
        cat_url = url_item['url']
        cat = url_item['cat']

        print("Processing:",cat,"-",cat_url)

        #//*** Load the Base Page scrape stories until Target Date is less that Story Date
        urls = get_all_urls_in_page(cat_url,tgt_date,False)

        #//**** Download the story for url
        for index,url in enumerate(urls):
            print(index+1,"/",len(urls),"- Downloading:",url)
        
            story = get_story(url,cat)

            #//**** Skip Processing Any Story with any error
            if story['error']:
                continue

            out.append(story)


            #wait between 1/2 to 3 seconds
            time.sleep(random.randint(500, 3000)/10000)  

        

    return out


def get_all_urls_in_page(source_url,tgt_date,headless=True):

    #//*** Keep all classnames in a dictionary
    g = {
        #//*** Classname for the Show More Button
        "class_more_button" : "show-button-more",
        
        #//*** Grid Classname that contains the linked stories
        "story_grid" : "grid3",
        
        #//*** Story Classes that contain the href Links
        "story_link_class" : "AnchorLink",
        
    }
    
    #//*** Initialize Headless Firefox options 
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')   
    
    if headless:


        #//*** Span Headless Instance
        driver = webdriver.Firefox(options=options)
    else:
        # run firefox webdriver from executable path of your choice
        driver = webdriver.Firefox()


    # Load Web Page
    driver.get(source_url)

    print("Page Loaded")
    
    # execute script to scroll down the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

    print("Scroll to Show More")

    #//*****************************************************
    #//*** Wait until the Show More Button is loaded
    #//*****************************************************
    elements = []
    control = 0
    while len(elements) == 0:

        #//*** Page is Loaded when class_more_button is displayed
        #elements = driver.find_elements_by_class_name(g["class_more_button"])
        elements = driver.find_elements(By.CLASS_NAME,g["class_more_button"])

        control += 1
        #//*** Wait if element not found
        if len(elements) == 0:
            time.sleep(1)

        if control > 15:
            print("Show More Button Not Loaded!")
            return
            break

    #//*************************************************
    #//*** The first elements is the button to click
    #//*************************************************
    elem_show_more = elements[0]

    #actions = ActionChains(driver)
    #actions.move_to_element(element).perform()

    print(elem_show_more.is_displayed())
    print(elem_show_more.location['y'])
    
    #results = driver.find_elements_by_class_name(g["story_grid"])[0].find_elements_by_class_name(g["story_link_class"])
    results = driver.find_elements(By.CLASS_NAME,g["story_grid"])[0].find_elements(By.CLASS_NAME,g["story_link_class"])

    if len(results) > 0:
        print("Last Page: ", results[0].get_property('href'))

    
    
    #print(results[-1].get_property('href'))

    
    #print(story_time,tgt_date, story_time < tgt_date)
                                                                        
    #//*** Get the last url to check in stories are within the quarter
    last_url = results[-1].get_property('href')
    print("last_url:",last_url)

    try:
        #//*** Download the last script
        last_script = get_story(last_url)
    except:
        print("Problem getting last script")
        print("Last url: ", last_url)
        print("get Scripts: ", get_story(last_url))
        print("Skipping..")
        return []
    last_date = last_script['epoch']
    print("Last Script: ", last_script['description'],"\n",last_script["date"])
    print("Last Script: ", last_script['epoch'] < tgt_date)
    
    #//***** Click SHOW MORE until Last Script is past Target Date
    #//*******************************************************************

    #//*** Maximum number of while loops.
    maxDepth = 20
    depth = 0
    
    #//*** Click Show More until Last Story is older than the tgt_date
    while last_date > tgt_date:
        depth += 1
        
        #//*** Scroll to Bottom of page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        
        print(f"Clicking More Depth: {depth}")
        #print(dir(elem_show_more))
        time.sleep(1)
        while elem_show_more.is_displayed() == False:
            print("Is Displayed:",str(elem_show_more.is_displayed()))
            time.sleep(5)
        
        
        try:
            #//*** Click Show More
            elem_show_more.click()
        except:
            iframes = driver.find_elements_by_tag_name("iframe")
            for iframe in iframes:
                print(iframe.get_property("name"))
                
                
                driver.execute_script("arguments[0].style.visibility='hidden'", iframe)
            #//*** Click Show More
            elem_show_more.click()
                
        #    return

    
        #//*** Get Updated Results
        #results = driver.find_elements_by_class_name(g["story_grid"])[0].find_elements_by_class_name(g["story_link_class"])        
        results = driver.find_elements(By.CLASS_NAME,g["story_grid"])[0].find_elements(By.CLASS_NAME,g["story_link_class"])        
        
        #//*** Get the last url to check in stories are within the quarter
        last_url = results[-1].get_property('href')


        try:
            #//*** Download the last script
            last_script = get_story(last_url)
        except:
            print("Problem getting last script")
            print("Last url: ", last_url)
            print("get Scripts: ", get_story([last_url]))
            print("Skipping..")
            return []
                
        last_date = last_script['epoch']
        print("Last Script: ", last_script['description'],"\n",last_script["date"])
        print("Last Script: ", last_script['epoch'] < tgt_date)
 
        if depth > maxDepth:
            print("Maximum Depth Reached on Clicking Show More")
            break
    
    print("This Should be True: ",last_date <= tgt_date)
   
    out = []
    
    for result in results:
        out.append(result.get_property('href'))
    
    print("Shutting Down Web Driver")
    #//*** Shut down main scrape
    driver.quit()
    
    

    return out

#//*** Download a Story using Requests and return a processed story
def get_story(url,cat=None):

    #//*** Download Page Source Using Requests
    r= requests.get(url)

    #//*** Initialize Output Story
    out = {
        "title" : "",
        "url" : "",
        "epoch" : -1, #//**** Int Formatted Epoch Time
        "date" : "",  #//**** String Formatted Date
        "datetime" : None, #//**** datetime Format Date
        "description" : "",
        "body" : "",
        "error" : False,
        "cat" : cat,

    }

    #//*** Extract the Javascript Text containing target JSON
    results = re.findall('<script type="text/javascript">.+</script>',r.text)

    if len(results) == 0:
        #//*** Throw some error message that says we can't work with this script
        print("===============")
        print("Error:")
        print("Function: get_story")
        print(url)
        print()
        print("Unable to Extract top level Javascript using Regex From Requests Page Source.")
        print("Looks like something is fundamentally Broken! Most Likely the page format changed or this link is an aberration.")
        out['error']=True
        return out

    #//*** Find the script containing the Juicy JSON 
    for raw in results:
        if "window['__abcotv__']" in raw:
            #//*** Strip Javascript tags from raw text
            raw = raw.replace('<script type="text/javascript">',"").replace("</script>","")[:-1]
            raw = raw[raw.index("=")+1:]
            #//*** Build an Object
            obj = json.loads(raw)
            
            #Need to find 'firstPub'
            #obj['page']['type']=='prism-story'

            out['title'] = obj['page']['meta']['title']
            out['url'] = obj['page']['meta']['canonical']
            out['description'] = obj['page']['meta']['metaDescription']
            

            #find and replace &#39; with '
            for x in obj['page']['content']['articleData']['mainComponents']:
                
                if 'name' in x.keys():
                    if 'Body' in x['name']:
                        if 'props' in x.keys():
                            #print(x['props'].keys())
                            
                            if 'body' in x['props'].keys():
                                
                                if len(x['props']['body']) == 1:
                                    for line in x['props']['body'][0]:
                                        
                                        if 'type' in line.keys():
                                            if line['type'] == 'p':
                                                if 'content' in line.keys():
                                                    if len(line['content']) == 1:
                                                        
                                                        #//*** Only Grab String Content
                                                        if isinstance(line['content'][0],str):
                                                            out['body'] += line['content'][0] + "\n"
                                                        
                                                else:
                                                    print("Missing Line Content in Story")
                                                continue
                                                
                                        else:
                                            print("Missing Type Line")
                                            continue
                                else:
                                    pass
                    else:
                        continue

                #//**** Get Published Time Value
                for x in obj['page']['content']['articleData']['mainComponents']:
                        if 'name' in x.keys():
                            if x['name'] == "ShareByline":
                                if 'props' in x.keys():
                                    if 'publishedDate' in x['props'].keys():
                                        
                                        if 'date' in x['props']['publishedDate']:
                                            
                                            #print(x['props']['publishedDate']['date'])
                                            #//*** Epoch Time is 14 characters, the built-in function requires 10.
                                            #//*** Convert to String, Grab the First 10 digits, then Convert back to an int
                                            epoch_time = int(str(x['props']['publishedDate']['date'])[:10])
                                            time_val = datetime.date.fromtimestamp(epoch_time)
                                            out['epoch'] = epoch_time
                                            out['datetime'] = time_val
                                            out['date'] = str(time_val)
                                        else:
                                            print("Missing Date Field from the Published Date Key ")
                                        
                                    else:
                                        print("Missing Published Date Field under ShareByLine")
                                else:
                                    print("Missing Props field in ShareByLine")
                                    continue
                            else:
                                continue
                        else:
                            continue
    
                #print("Title: " + out['title'])
                #print("Description: " + out['description'])
                #print("url: " + out['url'])
                #print("Epoch: "+ str(out['epoch']) + ":" + out['date'])
                #print("Text: "+ out['body'])

                return(out)

