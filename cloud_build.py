from google.cloud.devtools import cloudbuild_v1
from helper import send_cloud_build_failed_email, send_cloud_build_success_email
import logging


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
        def upload_model(get_project_id, get_trigger_id):
            logging.info("Task: Making Client Connection: ")
            cloud_build_client = cloudbuild_v1.CloudBuildClient()

            logging.info("Task: Triggering Cloud Build For Dolly Model Serving Container")
            response = cloud_build_client.run_build_trigger(project_id=get_project_id, trigger_id=get_trigger_id)

            if response.result():
                logging.info("Cloud Build Successful")
                return True
            else:
                logging.info("Cloud Build Failed !")
                raise RuntimeError

        try:
            if upload_model(project_id, trigger_id) is True:
                logging.info("Cloud Build completed successfully passing to next component")
                logging.error(f"Sending Cloud Build Success Email to: {receiver_email}")
                send_cloud_build_success_email(project_id, pipeline_name, user_email, user_email_password,
                                               receiver_email)

        except Exception as exc:
            logging.error("Some error occurred in upload model component!")
            logging.error(f"Sending Cloud Build Failure Email to: {receiver_email}")
            send_cloud_build_failed_email(project_id, pipeline_name, user_email, user_email_password,
                                          receiver_email)
            raise exc


project = "llm-dolly"
pipeline = "this-is-pipeline-name"
trigger = "9678a589-7df5-459e-bda8-b12579a8298f"
component = True
email = "kubeflow35@gmail.com"
password = "bodlerhhhuisjtgo"
receiver = 'aman.srivastava@knoldus.com'

upload_container(project, pipeline, trigger, component, email, password, receiver)