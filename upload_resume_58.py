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

class New_Linkedin_Scrapper:
    
    def __init__(self, data):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 30)
        sleep(5)

        self.json_data = data
        self.download_dir = os.path.join(os.getcwd(), 'Resume')
        if os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)
        os.makedirs(self.download_dir)

    def login(self):
        self.driver.get("https://www.linkedin.com/login")

        # Login credentials
        email = "Zuber.Ahmad@autviz.in"
        password = "Zubair@2023"

        
        email_field = self.wait.until(EC.element_to_be_clickable((By.ID, "username")))
        email_field.send_keys(email)
        sleep(2)

        password_field = self.wait.until(EC.element_to_be_clickable((By.ID, "password")))
        password_field.send_keys(password)
        sleep(5)

        login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()
        sleep(30)
        try:
            if  "challenge" in self.driver.current_url:
                print("Captcha not solved line-no 249")
                #Let’s do a quick security check
                self.driver.close()
                # return 400  # Return status code indicating failure
                return jsonify({"error": "CAPTCHA not solved"}), 500
            
            # elif :
            #     print("Your account has been temporary blocked.")
            #     self.driver.close()
            
            elif self.driver.current_url == "https://www.linkedin.com/feed/":

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
                            
                            if api_resume_url:
                                self.upload_resume(api_resume_url)

                else:
                    sleep(10)
                    self.upload_resume(api_resume_url)
                        
            else:
                print("Wrong email or password .")
                self.driver.close()
                # return 401  # Unauthorized status code
                return jsonify({"error": "Wrong email or password"}), 401
            
        except Exception as e:
            print("Login failed:")
            sleep(10)
            self.driver.close()
            # return 500  # Internal server error status code
            return jsonify({"error": "Login failed due to an exception."}), 500

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
        print("filename= ",filename)
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

