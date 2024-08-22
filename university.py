import requests
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import docx
from PyPDF2 import PdfReader
from selenium.webdriver.support.ui import Select
# import undetected_chromedriver as uc

class New_Linkedin_Scrapper:
    
    def __init__(self, data):
        self.driver = webdriver.Chrome()
        # self.driver = uc.Chrome()
        # self.wait = WebDriverWait(self.driver, 30)
        self.wait = WebDriverWait(self.driver, 10)
        # sleep(5)

        self.json_data = data

        self.download_dir = os.path.join(os.getcwd(), 'Resume')
        if os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)
        os.makedirs(self.download_dir)

    def login(self):

        # all_questions = self.json_data['Optional_Filters'][0]['answers'].get('allQuestions', [])
        # print('all_questions=',all_questions)
        # sleep(5)
        # self.driver.close()

        self.driver.get("https://www.linkedin.com/login")

        # Login credentials

        # email = "Zuber.Ahmad@autviz.in"   # Active
        # password = "Zubair@2023"

        user_data = self.json_data['Optional_Filters'][0]
        
        email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "username")))
        email_field.send_keys(user_data['email'])
        sleep(2)

        password_field = self.wait.until(EC.element_to_be_clickable((By.ID, "password")))
        password_field.send_keys(user_data['password'])
        sleep(5)

        login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()
        sleep(60)
        try:
            if  "challenge" in self.driver.current_url:
                print("Captcha not solved line-no 249")
                #Let’s do a quick security check
                self.driver.close()
                # return 400  # Return status code indicating failure
                return jsonify({"error": "CAPTCHA not solved"}), 500
            
            # elif "blocked" in self.driver.page_source.lower():
            #     print("Account temporarily blocked. Closing driver.")
            #     self.driver.close()
            #     return {"error": "Your account has been temporarily blocked"}
                
            elif self.driver.current_url == "https://www.linkedin.com/feed/":
                print("Login successfully")

                self.apply_jobs()

                self.driver.close()
                print("Complete Job apply process.")
                # print("Captcha Solved line-no 232")
                
                self.driver.get("https://www.linkedin.com/jobs/application-settings/?hideTitle=true")
                
                if self.json_data['applygenieResume'] == "":
                    try:
                        dropdown_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".jobs-resume-card__options-button-container .artdeco-dropdown:first-of-type"))
                        )
                        if dropdown_button:
                            print("CV found \n")
                            sleep(10)
                            self.download_resume_and_get_file_path()
                        else:
                            print("CV not found.")
                            print("Please send me resume link...")
                            sleep(60)
                            
                            print("else condition",api_resume_url)
                            if api_resume_url:
                                self.upload_resume(api_resume_url)
                    except Exception as e:
                            print(f"Exception condition: {str(e)}")   
                            print("CV not found.")
                            print("Please send me resume link...")                             
                            sleep(60)
                            
                            #CV-NOT-FOUND Api hit to find resume link 
                            if api_resume_url:
                                self.upload_resume(api_resume_url)

                else:
                    sleep(10)
                    self.upload_resume(api_resume_url)
                        
            else:
                print("Wrong email or password.")
                self.driver.close()
                # return 401  # Unauthorized status code
                return jsonify({"error": "Wrong email or password"}), 401
            
        except Exception as e:
            print("Login failed:")
            sleep(5)
            self.driver.close()
            # return 500  # Internal server error status code
            return jsonify({"error": "Login failed due to an exception."}), 500

    def apply_jobs(self):
        global job_url
        job_urls = self.json_data.get('job_search_urls', [])
        for job in job_urls:
            job_url = job.get("url")
            is_save = job.get("IsSave")
            # print("job_url=128", job_url)
            if is_save:
                self.save_job(job_url)
            else:
                self.apply_to_job(job_url)
    def save_job(self,job_url):
        # print("Inside Save Jobs Functionality...")
        self.driver.get(job_url)
        sleep(5)
        # try:
        save_button = self.wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "jobs-save-button"))
        )
        if save_button:
            print("Save Button found.")
            save_button.click()
            sleep(5)
            print("Job has been saved for url:",job_url)
        else:
            print("Save Button Not Found.")
        # except Exception as e:
        #     print(f"Failed to save the job: {str(e)}")

    def apply_to_job(self,job_url):
        # print("Inside Job Apply Functionality...")
        
        self.driver.get(job_url)
        easy_apply_button = self.wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "jobs-apply-button"))
                )               

        if easy_apply_button:
            print("Easy Apply Button Found.")
            easy_apply_button.click()
            # print("Clicked on easy apply button...")
            sleep(2)

            self.get_user_profile_page_data()

        else:
            print("Easy Apply button not found.")    

    def mobile_number(self):
        new_phone_number = self.json_data["Optional_Filters"][0]['Name_Category']['number']

        try:
            # Try to find and clear the 'Phone' input field
            phone_input = self.driver.find_element_by_xpath("//label[contains(text(),'Phone')]/following-sibling::input")
            phone_input.clear()
            phone_input.send_keys(new_phone_number)
            
        except:
            try:
                # If 'Phone' input field not found, try 'Mobile phone number'
                phone_input = self.driver.find_element(By.XPATH, "//label[contains(text(),'Mobile phone number')]/following-sibling::input")
                phone_input.clear()
                phone_input.send_keys(new_phone_number)
                
            except:
                # If both labels fail, find the input field by its class name and update it
                Mobile_number = self.driver.find_element(By.CLASS_NAME, "artdeco-text-input--label").get_attribute("innerHTML")
                if "Mobile" in Mobile_number or "phone" in Mobile_number:
                    New_number = self.driver.find_element(By.CSS_SELECTOR, "input.artdeco-text-input--input")
                    New_number.clear()
                    New_number.send_keys(new_phone_number)

    def get_user_profile_page_data(self):
        # print("Inside User info function")
        # sleep(2)        
        
        try:
            # Update mobile phone number
            self.mobile_number()
        except:
            pass

        #User Profile Page(Click on next button) 
        self.useful_button("next")
        sleep(2)

        #Resume Page(Click on next button)
        try:
            self.useful_button("next")
            sleep(2)
            print("Clicked on next button.")
        except:
            pass

        # #Resume Page(Click on review button)
        # try:
        #     self.useful_button("review")
        #     sleep(2)
        #     print("Clicked on review button.")
        # except:
        #     pass

        # #Review Page(Click on submit application button)
        # try:
        #     self.useful_button("submit application")
        #     print("Clicked on submit application button.")
        #     print("212 Job successfully applied for url:",job_url)
        #     sleep(2)
        # except:
        #     pass

        # try:
        #     self.useful_button("done")
        #     sleep(2)
        #     print("220 Job successfully applied for url:",job_url)
        # except:
        #     pass

        try:
            checking_all_form_fields = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")

            self.auto_answers(checking_all_form_fields)

        except:
            pass

        try:
            self.useful_button("next")
            sleep(2)
            print("Clicked on next button.")
        except:
            pass

        #Work Authorization Page
        try:
            self.work_authorization()
        except:
            pass

        try:
            self.useful_button("review")
            sleep(5)
        except:
            pass


        #Review Page(Click on submit application button)
        try:
            self.useful_button("submit application")
        except:
            pass

        try:
            self.useful_button("done")
        except:
            pass
        
        # print("Job applied successfully for url:",job_url)

                
    def useful_button(self, button_name):
        # print("job_url=286",job_url)
        sleep(2)
        try:
            # Find all elements with class name "artdeco-button"
            all_elems = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "artdeco-button")))
            # print("all_elems",len(all_elems))
            # Iterate through the found elements
            for elem in range(len(all_elems)):
                # Check if the button_name is in lowercase within the element's text
                if button_name in all_elems[elem].text.lower():
                    # Click on the button
                    all_elems[elem].click()
                    if button_name == 'submit application':
                        print("432 Job applied successfully for url:", job_url)
                    return True
                
        except Exception as e:
            # Print an error message if there is an exception
            # print(f'useful button error: {e}')
            pass
        
        # Return False if the button was not found or clicked
        return False
 
    def auto_answers(self, checking_all_form_fields):
        # print("Inside auto answer")
        question_data = []
        failed_questions = []  # To store questions with no answers
        for form_fields in range(len(checking_all_form_fields)):

            # print("Inside loop.")
            
            try:
                # Check if the input type is radio button
                radio_attr = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[form_fields].find_element(By.TAG_NAME, "input").get_attribute("type")
                if radio_attr == "radio":
                    print("Question type is radio.")
                    # Get the question text
                    quest = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[form_fields].find_element(By.TAG_NAME, "legend").text.lower()

                    quest= quest.split('\n')[0]

                    # print("radio quest-305", quest)

                    question_data.append({"type":radio_attr,"question": quest})                    
                    
                    answer = self.get_answer_from_json(radio_attr, quest)
                    # print("answer-307", answer)

                    # answer = False
                    if answer is not False: #Question found in json
                        # Click on the appropriate label based on the answer
                        if answer.lower() == "no":
                            self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[
                                form_fields].find_elements(By.TAG_NAME, "label")[-1].click()
                            
                        else: #answer.lower() == "yes":
                            self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[
                                form_fields].find_element(By.TAG_NAME, "label").click()
                    else:
                        # If no specific answer, select the first option by default
                        #yes set karenge
                        self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[form_fields].find_element(By.TAG_NAME, "label").click()
                
                # else:
                #     # Handle other types of input fields
                #     self.driver.find_elements(By.CLASS_NAME, "mannhuwa")[form_fields].find_element(By.TAG_NAME,"input").get_attribute("mannhuwa")
            except:
                # print("341")
                # radio_attr = "select"
                # Handle cases where a select dropdown is present
                if "select an option" in checking_all_form_fields[form_fields].text.lower():

                    print("Question type is Dropdown.")

                    quest = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[
                        form_fields].find_element(By.TAG_NAME, "label").text.lower()
                    
                    quest= quest.split('\n')[0]

                    # print("Dropdown question=",quest)

                    question_data.append({"type":"select","question": quest})

                    answer = self.get_answer_from_json(radio_attr, quest)
                    
                    # answer == False
                    if answer == False :
                        # Select a default option if no specific answer is found
                        sleep(1)
                        select_element = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[
                            form_fields].find_element(By.TAG_NAME, "select")
                        select = Select(select_element)
                        select.select_by_index(1)
                        if select.first_selected_option.text == "None":
                            select.select_by_index(2)
                    else:
                        # Select the answer based on predefined logic
                        select_element =  self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[
                            form_fields].find_element(By.TAG_NAME, "select")
                        select = Select(select_element)
                        main_answer = answer.title()
                        select.select_by_value(main_answer)
                else:
                    try:
                        # If neither radio nor select, handle as text input
                        # if radio_attr == "text":
                        print("Question type is text.")
                        quest = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[
                            form_fields].find_element(By.TAG_NAME, "label").text.lower()
                        
                        # print("text quest-399=", quest)
                    
                        question_data.append({"type":radio_attr,"question": quest})

                    except:
                        pass
                    try:
                        # Attempt to answer based on predefined logic for text inputs
                        radio_attr = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[form_fields].find_element(By.TAG_NAME, "input").get_attribute("type")
                       
                        # print("415 radio_attr=",radio_attr)

                        answer = self.get_answer_from_json(radio_attr, quest)
                        # print("answer-421", answer)

                        if answer == False :

                            print("No answer found for question:", quest)
                            failed_questions.append({"type": radio_attr, "question": quest, "url": job_url})
                            # print("Job has been failed for url:", job_url)
                        else:
                            # Input the found answer into the text field
                            text_box_element = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")[form_fields].find_element(By.TAG_NAME, "input")
                            text_box_element.clear()
                            text_box_element.send_keys(answer)
                    except Exception as e:
                        print("jobs-easy-apply-form-section__grouping error 2521" )

        # print("job_url=", job_url)
        # print("question_data=", question_data)

        if failed_questions:
            print("Job not applied due to missing answers for the following questions:", failed_questions)
        # else:
            # print("432 Job applied successfully for url:",job_url)

    def get_answer_from_json(self, radio_attr, quest):
        Optional_Filters = self.json_data['Optional_Filters'][0]
        answers = Optional_Filters["answers"]
        all_questions = answers["allQuestions"]
        
        for all_ques in all_questions:

            print("Json_Question=", all_ques["question"])
            print("Linkedin_Question=", quest,'\n')

            # Check if the type matches and the question text matches
            if all_ques["type"] == radio_attr and all_ques["question"].strip().lower() == quest.strip().lower():
                print("Question found in JSON.")
                return all_ques['answer'] 
            # else:
            #     print("Question not found in JSON.")
        # If no matching question is found, return False
        return False

    def work_authorization(self):
        print("Inside Work authorization.")
        try:
            # Check if 'work authorization' is present in the section title
            if "work authorization" in self.driver.find_element(By.CLASS_NAME, "pb4").find_element(By.TAG_NAME, "h3").text.lower():
                # Find all form field groupings within the section
                checking_all_form_fields = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")
                
                # Automatically answer the form fields
                self.auto_answers(checking_all_form_fields)
                                
        except:
            pass  # Ignore any errors silently

    def upload_resume(self, api_resume_url):
        # print("Start resume uploading")
        try:
            resume_url = api_resume_url
            resume_file = self.download_resume_using_url_and_get_filepath(resume_url)  
            sleep(10)
            if resume_file:
                # print("Resume downloaded successfully and received file path")

                upload_resume_button = self.driver.find_element(By.CSS_SELECTOR, "label[for='resume-upload-button']")
                if upload_resume_button:
                    # print("Upload Resume Button Available")
                    file_input = self.driver.find_element(By.ID, "resume-upload-button")
                    file_input.send_keys(resume_file)
                    sleep(10)
                    
                    # print("Resume uploaded successfully on LinkedIn")
                    os.remove(resume_file)

                    self.download_resume_and_get_file_path()
                    sleep(10)

                    return 200  # Success response

                else:
                    print("Upload Resume Button not found")
                    return 500  # Fail response
            else:
                print("Failed to download resume file")
                return 500  # Fail response
        except Exception as e:
            return 500  # Fail response

    def download_resume_using_url_and_get_filepath(self, resume_url):
        try:
            local_filename = os.path.join(self.download_dir, resume_url.split("/")[-1])
            with requests.get(resume_url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            # print(f"Resume downloaded by url to: {local_filename}")
            return local_filename
        except Exception as e:
            print("Error downloading resume file:", e)
            return None

    def download_resume_and_get_file_path(self):
        # print("dowload 154")
        sleep(5)
        try:
            dropdown_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".jobs-resume-card__options-button-container .artdeco-dropdown:first-of-type"))
            )
            dropdown_button.click()          
            sleep(5)

            dropdown_content = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "artdeco-dropdown__content-inner")))

            dropdown_items = dropdown_content.find_elements(By.CLASS_NAME, "artdeco-dropdown__item")

            download_button = None

            for item in dropdown_items:
                if item.text.strip() == "Download":
                    # print("Download button found line-no 335 \n")
                    download_button = item
                    break

            if download_button:
                download_button.click()
                sleep(10)

                download_dir = os.path.expanduser("~\\Downloads")
                files = os.listdir(download_dir)

                if files:
                    latest_file = max([os.path.join(download_dir, f) for f in files], key=os.path.getctime)
                    
                    if latest_file:                        
                        resume_text = self.getText(latest_file)
                        print(resume_text)
                        sleep(2)
                        os.remove(latest_file)
                        return 200  # current code
                    else:
                        print("no filepath get")

                else:
                    print("Download failed, no file found in download directory")
            else:
                print("Download button not found line-145")
        except Exception as e:
            print("Something went wrong while downloading resume line-147:")
        finally:
            self.driver.close()

    def getText(self, filename):
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension == '.docx':
            doc = docx.Document(filename)
            fullText = []
            
            for element in doc.element.body:
                if element.tag.endswith('p'):  
                    fullText.append(element.text)
                elif element.tag.endswith('tbl'):  
                    table_text = []
                    table = docx.table.Table(element, doc)
                    for row in table.rows:
                        row_text = [cell.text for cell in row.cells]
                        table_text.append('\t'.join(row_text))
                    fullText.append('\n'.join(table_text))
            return '\n'.join(fullText)
        
        elif file_extension == '.pdf':
            # print("File is pdf")
            reader = PdfReader(filename)
            fullText = []
            
            for page in reader.pages:
                fullText.append(page.extract_text())
            return '\n'.join(fullText)
        else:
            return "Unsupported file type"


from flask import Flask, request, jsonify
app = Flask(__name__)

api_resume_url = None

@app.route('/resume-url', methods=['POST'])
def upload_resume():
    global api_resume_url  # Declare the variable as global to modify it
    try:
        data = request.get_json()
        api_resume_url = data.get("applygenieResume")

        if data:
            # print("Json data received...")
            obj = New_Linkedin_Scrapper(data)
            obj.login()
            # print(f"Received resume URL line-168: {api_resume_url}")

            # print("Resume uploaded successfully 173")

            return jsonify({"message": "Resume uploaded successfully line-276"}), 200
        else:
            print("No json data provided...")
            return jsonify({"error": "No json data provided"}), 400

    except Exception as e:
        sleep(5)
        return jsonify({"error": "Something went wrong."}), 500

@app.route('/CV-NOT-FOUND', methods=['POST'])
def CV_NOT_FOUND():
    global api_resume_url  
    try:
        data = request.get_json()
        api_resume_url = data.get("applygenieResume")
        
        if api_resume_url:

            return jsonify({"message": "Resume URL processed successfully"}), 200
        else:
            print("No resume URL provided")
            return jsonify({"error": "No resume URL provided"}), 400

    except Exception as e:
        return jsonify({"error": "Something went wrong."}), 500

if __name__ == '__main__':
    app.run(debug=False)

