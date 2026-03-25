import boto3
import time
from datetime import datetime


class EC2Manager:
    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)

    def create_instance(self):
        print("Launching EC2 instance...")

        response = self.ec2.run_instances(
            ImageId='ami-0c02fb55956c7d316',  # Amazon Linux 2
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'Interview-Instance'},
                        {'Key': 'Environment', 'Value': 'Dev'}
                    ]
                }
            ]
        )

        instance_id = response['Instances'][0]['InstanceId']
        print(f"Instance created: {instance_id}")
        return instance_id

    def wait_for_running(self, instance_id):
        print("Waiting for instance to enter running state...")

        while True:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            state = response['Reservations'][0]['Instances'][0]['State']['Name']

            print(f"Current state: {state}")

            if state == 'running':
                print("Instance is now running!")
                break

            time.sleep(5)

    def get_instance_info(self, instance_id):
        response = self.ec2.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]

        public_ip = instance.get('PublicIpAddress', 'N/A')
        launch_time = instance['LaunchTime']

        print(f"Public IP: {public_ip}")
        print(f"Launch Time: {launch_time}")

    def stop_instance(self, instance_id):
        print("Stopping instance to save cost...")

        self.ec2.stop_instances(InstanceIds=[instance_id])

        print("Instance stop initiated.")


def log_event(message):
    with open("deployment_log.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] {message}\n")


def main():
    manager = EC2Manager()

    try:
        instance_id = manager.create_instance()
        log_event(f"Created instance: {instance_id}")

        manager.wait_for_running(instance_id)
        log_event(f"Instance running: {instance_id}")

        manager.get_instance_info(instance_id)

        # Wait before stopping (simulate usage)
        print("Simulating workload for 20 seconds...")
        time.sleep(20)

        manager.stop_instance(instance_id)
        log_event(f"Stopped instance: {instance_id}")

    except Exception as e:
        print("Error occurred:", str(e))
        log_event(f"Error: {str(e)}")


if __name__ == "__main__":
    main()