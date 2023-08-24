from google.cloud.devtools import cloudbuild_v1
from helper import send_cloud_build_failed_email, send_cloud_build_success_email
import logging
import time


def upload_model(get_project_id, get_trigger_id):
    logging.info("Task: Making Client Connection: ")
    cloud_build_client = cloudbuild_v1.CloudBuildClient()

    logging.info("Task: Triggering Cloud Build For Dolly Model Serving Container")
    response = cloud_build_client.run_build_trigger(project_id=get_project_id, trigger_id=get_trigger_id)

    logging.info(f"Cloud Build Trigger Execution Status: {response.running()}")

    logging.info("Task: Extracting cloud build metadata")
    trigger_details = response.metadata
    build_data = trigger_details.build

    logging.info("Task: Extracting logs url from build metadata")
    log_path = build_data.log_url

    logging.info("Task: Extracting build running status from build metadata")
    running_status = response.running()

    while running_status:
        logging.info("Task: Checking Cloud Build Status:")
        running_status = response.running()
        done_status = response.done()

        logging.info(f"Build Running: {running_status} & Build Done: {done_status}")
        if not running_status and done_status is True:
            break

        time.sleep(5)

    logging.info("Task: Extracting latest metadata of cloud build")
    trigger_details = response.metadata
    build_data = trigger_details.build

    logging.info("Task: Extracting build execution status from build metadata")
    build_status = build_data.status
    status_check = str(build_status).split('.')[-1]

    logging.info(f"Task: Checking Cloud Build Status: {status_check}")
    if status_check == "SUCCESS":
        logging.info("Task: Returning True for cloud build status")
        return True, log_path
    elif status_check == "FAILED":
        logging.info("Task: Returning False for cloud build status")
        return False, log_path


def upload_container(project_id: str,
                     pipeline_name: str,
                     trigger_id: str,
                     component_execution: bool,
                     user_email: str,
                     user_email_password: str,
                     receiver_email: str
                     ):
    logger = logging.getLogger('tipper')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    if not component_execution:
        logging.info("Component execution: upload serving container image is bypassed")
    else:
        try:
            status, logs = upload_model(project_id, trigger_id)

            if isinstance(status, bool) and status:
                logging.info(f"Sending Cloud Build Success Email to: {receiver_email}")
                send_cloud_build_success_email(project_id,
                                               pipeline_name,
                                               user_email,
                                               user_email_password,
                                               receiver_email,
                                               str(logs))
            else:
                logging.error(f"Sending Cloud Build Failure Email to: {receiver_email}")
                send_cloud_build_failed_email(project_id,
                                              pipeline_name,
                                              user_email,
                                              user_email_password,
                                              receiver_email,
                                              str(logs)
                                              )
                raise RuntimeError

        except Exception as exc:
            logging.error("Some error occurred in upload model component!")
            raise exc


project = "llm-dolly"
pipeline = "this-is-pipeline-name"
trigger = "9678a589-7df5-459e-bda8-b12579a8298f"
component = True
email = "kubeflow35@gmail.com"
password = "bodlerhhhuisjtgo"
receiver = 'aman.srivastava@knoldus.com'

upload_container(project, pipeline, trigger, component, email, password, receiver)
