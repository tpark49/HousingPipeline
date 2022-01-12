import datetime
import logging
import azure.functions as func
from selenium import webdriver
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from azure.storage.blob import ContainerClient
import os


def scrape_urls(list_of_zipcodes):
    url = [] 
    for zipcode in list_of_zipcodes: 
        
#         global stop_threads_1
#         if stop_threads_1: 
#             break
        #print("urls", end="")
        #print(len(list_of_zipcodes[:list_of_zipcodes.index(zipcode)+1])/len(list_of_zipcodes))
        print(zipcode)
        driver = webdriver.Chrome("/tmp/chromedriver/chromedriver",options=chrome_options)
        driver.get(f"https://www.redfin.com/zipcode/{zipcode}")
        try:
            url += [x.get_attribute("href") for x in driver.find_elements_by_xpath("//div[@class='PhotoSlider photoContainer']//a")]
        except Exception as e:
            print(e)

        try: 
            total_pages = [x.get_attribute("href") for x in driver.find_elements_by_xpath("//a[@class='clickable goToPage']")]

            if total_pages and len(total_pages)>=1: 
                for page in total_pages:
                    driver.get(page)
                    url += [x.get_attribute("href") for x in driver.find_elements_by_xpath("//div[@class='PhotoSlider photoContainer']//a")]
            driver.close()
            

        except Exception as e: 
            print(e)
            
    return url


def scrape_features(list_of_urls):

    
    fullpath = '/tmp/' +  datetime.today().strftime('%Y-%m-%d') + str(parent_number) + str(batch_number) + '.csv'
    with open(fullpath, 'a', newline='') as csvfile:
        fieldnames = ["address","State_zipcode","last_checked","last_updated","price","bed","bath",
                      "square_footage","description","status","time_on_redfin","property_type","HOA_dues",
                      "commission","year_built","community","lot_size","MLS","list_price","ppsf","redfin_est",
                      "walk","train","bike","act_views","act_favs","act_outs","act_tours","mkt_score",
                      "mkt_rating", "pub_beds","pub_baths","pub_fin_sqft","pub_unfin_sqft","pub_total_sqft",
                      "pub_stories","pub_lot_size","pub_style","pub_yr_built","pub_yr_reno","pub_county",
                      "pub_apn", "style","lat","long","agent_name","agent_company","url"
                     ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        

#         driver = webdriver.Chrome("/tmp/chromedriver/chromedriver", options = chrome_options)
        for single_url in list_of_urls:
            
#             global stop_threads_2
#             if stop_threads_2:
#                 break
            print(single_url)
#             print("list of urls", end="")
#             print(len(list_of_urls[:list_of_urls.index(single_url)+1])/len(list_of_urls))
#             print(list_of_urls.index(url), end='/r')
            driver = webdriver.Chrome("/tmp/chromedriver/chromedriver", options = chrome_options)
            driver.get(single_url)
            
            # ADDRESS SCRAPE
            try:
                address = driver.find_element_by_xpath("//div[@class='street-address']").text
            except NoSuchElementException:
                address = driver.find_element_by_xpath("//meta[@name='twitter:text:street_address']").get_attribute("content")
            except Exception:    
                address = None
                print("no address, " + single_url)
            
            # STATE/ZIPCODE SCRAPE
            try:
                State_zipcode = driver.find_element_by_xpath("//div[@class='dp-subtext']").text
            except:
                State_zipcode = None
                print("no state/zip, " + single_url)
                
            # PRICE/BED/BATH SCRAPE
            try:
                element_pricebedsbath = driver.find_elements_by_xpath("//div[@class='statsValue']")
                price = element_pricebedsbath[0].text
                bed   = element_pricebedsbath[1].text
                bath  = element_pricebedsbath[2].text
            except:
                price = None
                bed   = None
                bath  = None
                print("no price/bed/bath, " + single_url)
                
            # SQUARE FOOTAGE SCRAPE
            try:
                square_footage = driver.find_element_by_xpath("//span[@class='statsValue']").text
            except NoSuchElementException:
                square_footage = driver.find_element_by_xpath("//meta[@name='twitter:text:sqft']").get_attribute("content")          
            except Exception:
                square_footage = None
                print("no square footage, " + single_url)
                                
            # DESCRIPTION SCRAPE
            try:
                description = driver.find_element_by_xpath("//p[@class='text-base']//span").text
            except NoSuchElementException:
                description = driver.find_element_by_xpath('//meta[@name="twitter:text:description_simple"]').get_attribute("content")
            except Exception:
                description = None
                print("no description, " + single_url)
                    
            # LAST CHECKED SCRAPE
            try:
                last_checked = driver.find_element_by_xpath("//div[@class='data-quality']/a").text
            except:
                last_checked = None
                print("no last checked, " + single_url)
                
            # LAST UPDATED SCRAPE
            try:
                last_updated = driver.find_elements_by_xpath("//div[@class='data-quality']")[-1].text
            except NoSuchElementException:
                element_last_update = driver.find_element_by_xpath('//div[@class="listingInfoSection font-color-gray-dark"]//div')
                checked, updated = element_last_update.text.split(' | ')
                last_updated = updated.replace('Last updated ', '')
            except Exception:
                last_updated = None
                print("last updated, " + single_url)
                
            # HOME FACTS TABLE SCRAPE
            home_facts = driver.find_elements_by_xpath("//div[@class='keyDetail font-weight-roman font-size-base']//span")
            
            # NULL all inital values
            status, time_on_redfin, property_type, HOA_dues, year_built, community, lot_size, MLS, list_price, ppsf, redfin_est, style, commission = (None,)*13
                
            for i in range(len(home_facts)):
                text = home_facts[i].text
        
                if text == "Status":
                    status = home_facts[i+1].text
                elif text == "Time on Redfin": 
                    time_on_redfin = home_facts[i+1].text
                elif text == "Property Type":
                    property_type = home_facts[i+1].text
                elif text == "HOA Dues":
                    HOA_dues = home_facts[i+1].text
                elif text == "Year Built":
                    year_built = home_facts[i+1].text
                elif text == "Community":
                    community = home_facts[i+1].text
                elif text == "Lot Size":
                    lot_size = home_facts[i+1].text
                elif text == "MLS#":
                    MLS = home_facts[i+1].text
                elif text == "List Price":
                    list_price = home_facts[i+1].text
                elif text == "Price/Sq.Ft.":
                    ppsf = home_facts[i+1].text
                elif text == "Redfin Estimate":
                    redfin_est = home_facts[i+1].text
                elif text == "Style":
                    style = home_facts[i+1].text
                elif text == "Buyer's Brokerage Commission":
                    commission = home_facts[i+1].text
            
            # TRANSPORTATION SCRAPE
            try:
                transport      = driver.find_elements_by_xpath('//div[@data-rf-test-name="ws-percentage"]')
                walk1, walk2   = transport[0].text.split('/')
                train1, train2 = transport[1].text.split('/')
                bike1, bike2   = transport[2].text.split('/')

                ## this will create a percentage of the commuting scores
                walk1  = float(walk1)
                walk2  = float(walk2)
                walk   = walk1/walk2
                train1 = float(train1)
                train2 = float(train2)
                train  = train1/train2
                bike1  = float(bike1)
                bike2  = float(bike2)
                bike   = bike1/bike2
            except:
                walk   = None
                train  = None
                bike   = None
                print("no transport, " + single_url)
            
            # ACTIVITY
            try:
                activity  = driver.find_elements_by_xpath("//div[@class='upperLabel']//span[@data-rf-test-name='activity-count-label']")
                act_views = activity[0].text
                act_fav   = activity[1].text
                act_outs  = activity[2].text
                act_tours = activity[3].text
            except:
                act_views = None
                act_fav   = None
                act_outs  = None
                act_tours = None
                print("no activity, " + single_url)               
            
            # MARKET SCORE/COMPETITION SCRAPE
            try:
                market = driver.find_element_by_xpath("//div[@class='scoreTM']")
                score_x, rating_x, redfin_x = market.text.split('\n')
                mkt_score  = score_x
                mkt_rating = rating_x
            except:
                print("no mkt comp, " + single_url)
                mkt_score  = None     
                mkt_rating = None
                
            # PUBLIC FACTS TABLE SCRAPE
            public_facts = driver.find_elements_by_xpath('//div[@class="facts-table"]//div[@class="table-row"]')

            # NULL all inital values
            beds1, baths1, fin_sqft, unfin_sqft, total_sqft, stories, lot_size, style, yr_built, yr_reno, county, apn = (None,)*12
            
            # this will iterate the table and assign the values to appropriate variables
            for idx, data in enumerate(public_facts):
                # data contains both the field and the value
                # this will split the data into 2 variables
                field, value = public_facts[idx].text.split('\n')

                if field == "Beds":
                    beds1 = value
                elif field == "Baths":
                    baths1 = value
                elif field == "Finished Sq. Ft.":
                    fin_sqft = value
                elif field == "Unfinished Sq. Ft.":
                    unfin_sqft = value
                elif field == "Total Sq. Ft.":
                    total_sqft = value
                elif field == "Stories":
                    stories = value
                elif field == "Lot Size":
                    lot_size = value
                elif field == "Style":
                    style = value
                elif field == "Year Built":
                    yr_built = value
                elif field == "Year Renovated":
                    yr_reno = value
                elif field == "County":
                    county = value
                elif field == "APN":
                    apn = value

            # now we append to add all values including blanks for the listing
            pub_beds       = beds1
            pub_baths      = baths1
            pub_fin_sqft   = fin_sqft
            pub_unfin_sqft = unfin_sqft
            pub_total_sqft = total_sqft
            pub_stories    = stories
            pub_lot_size   = lot_size
            pub_style      = style
            pub_yr_built   = yr_built
            pub_yr_reno    = yr_reno
            pub_county     = county
            pub_apn        = apn
            
            # LAT/LONG
            try:
                lat = json.loads(driver.find_element_by_xpath("//div[@class='Section AddressBannerSectionV2 white-bg not-omdp']//script").get_attribute('innerHTML'))["geo"]["latitude"]
                long = json.loads(driver.find_element_by_xpath("//div[@class='Section AddressBannerSectionV2 white-bg not-omdp']//script").get_attribute('innerHTML'))["geo"]["longitude"]
            except NoSuchElementException:
                geo_position = driver.find_element_by_xpath('//meta[@name="geo.position"]').get_attribute("content")
                lat_temp, long_temp = geo_position.split(";")
                lat  = float(lat_temp)
                long = float(long_temp)
            except Exception:
                lat  = None
                long = None
                print("no lat/long, " + single_url)
                
            # AGENT NAME
            try: 
                agent_name = driver.find_element_by_xpath("//span[@class='agent-name']").text
            except:
                agent_name = None 
                print("no agent name, " + single_url)
                
            # AGENT COMPANY
            try:
                agent_company = driver.find_element_by_xpath("//div[@class='aaq-question-stage-agent-info']//div").text
            except:
                agent_company = None
                print("no agent company, " + single_url)
                
            # PROPERTY DETAILS
#             try:
#                 property_details = driver.find_element_by_xpath('//*[@id="propertyDetails-collapsible"]/div[2]/div/div/div[1]').text
#             except:
#                 property_details = None
                    
            list_table = { 
                "address":address,"State_zipcode":State_zipcode,"last_checked":last_checked,
                "last_updated":last_updated,"price":price,"bed":bed,"bath":bath,
                "square_footage":square_footage,"description":description,"status":status,
                "time_on_redfin":time_on_redfin,"property_type":property_type,"HOA_dues":HOA_dues,
                "commission":commission,"year_built":year_built,"community":community,"lot_size":lot_size,
                "MLS":MLS,"list_price":list_price,"ppsf":ppsf,"redfin_est":redfin_est,"walk":walk,
                "train":train,"bike":bike, "act_views":act_views,"act_favs":act_fav,"act_outs":act_outs,
                "act_tours":act_tours,"mkt_score":mkt_score,"mkt_rating":mkt_rating,"pub_beds":pub_beds,
                "pub_baths":pub_baths,"pub_fin_sqft":pub_fin_sqft,"pub_unfin_sqft":pub_unfin_sqft,
                "pub_total_sqft":pub_total_sqft,"pub_stories":pub_stories,"pub_lot_size":pub_lot_size,
                "pub_style":pub_style,"pub_yr_built":pub_yr_built,"pub_yr_reno":pub_yr_reno,
                "pub_county":pub_county,"pub_apn":pub_apn,"style":style,"lat":lat,"long":long,
                "agent_name":agent_name,"agent_company":agent_company,
                "url":single_url
                }
                
            writer.writerow(list_table)
                
            driver.close()
        
    print("complete!")


def main(mytimer: func.TimerRequest) -> None:
    # utc_timestamp = datetime.datetime.utcnow().replace(
    #     tzinfo=datetime.timezone.utc).isoformat()

    #logging.info('Python timer trigger function ran at %s', utc_timestamp)
    logging.info("testing with my function")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})


    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    driver.get('https://www.redfin.com/zipcode/20002/')
    
    

    logging.info(driver.page_source)
    # print(driver.page_source)
    # links = driver.find_elements_by_tag_name("a")
    # link_list = ""
    # for link in links:
    #     if link_list == "":
    #         link_list = link.text
    #     else:
    #         link_list = link_list + ", " + link.text
    
    # create blob service client and container client
    # credential = DefaultAzureCredential()
    # storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
    # client = BlobServiceClient(account_url=storage_account_url, credential=credential)
    # blob_name = "test" + str(datetime.now()) + ".txt"
    # blob_client = client.get_blob_client(container=os.environ["par_storage_container_name"], blob=blob_name)
    # blob_client.upload_blob(link_list)



    # connection_string = f"DefaultEndpointsProtocol=https;AccountName={STORAGEACCOUNTNAME};AccountKey={STORAGEACCOUNTKEY};EndpointSuffix=core.windows.net"

    # container = ContainerClient.from_connection_string(conn_str=connection_string, container_name=CONTAINERNAME)

    # blob_list = container.list_blobs()
    # for blob in blob_list:
    #     print(blob.name + '\n')
