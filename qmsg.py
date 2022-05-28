import requests

class Robot:
    def __init__(self):
        self.ip = "106.52.3.250"
        self.port = "7600"

    def mail_private(self,user_id,msg):
        url = f"http://{self.ip}:{self.port}/send_private_msg"
        paylaod ={
            "user_id":user_id,
            "message":msg
        }
        response = requests.post(url, data=paylaod)
        print(response.text)

    def mail_group(self,group_id,msg):
        url = f"http://{self.ip}:{self.port}/send_group_msg"
        paylaod ={
            "group_id":group_id,
            "message":msg
        }
        response = requests.post(url, data=paylaod)
        print(response.text)
if __name__ == "__main__":
    robot = Robot()
    robot.mail_private(1137040634,"test")
