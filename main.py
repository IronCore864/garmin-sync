import logging
import os

from garminconnect import Garmin

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


cn_client = Garmin(
    os.environ.get("GARMIN_CN_EMAIL"),
    os.environ.get("GARMIN_CN_PASSWORD"),
    is_cn=True,
)
cn_client.login()
logger.info("Garmin CN login successful!")

logger.info("Get latest 3 activities from Garmin CN ...")
activities = cn_client.get_activities(0, 3)
logger.info("Get latest 3 activities from Garmin CN done!")

logger.info("Login to Garmin Global ...")
client = Garmin(
    os.environ.get("GARMIN_GLOBAL_EMAIL"), os.environ.get("GARMIN_GLOBAL_PASSWORD")
)
client.login()
logger.info("Garmin Global login successful!")

for activity in activities:
    try:
        logger.info(
            f"Activity {activity['activityId']}: {activity['activityName']}, started on {activity['startTimeLocal']}"
        )
        logger.info(f"Download activity {activity['activityId']} from Garmin CN ...")

        activity_bytes = cn_client.download_activity(activity["activityId"])
        activity_file = f"./{activity["activityId"]}.tcx"
        with open(activity_file, "wb") as f:
            f.write(activity_bytes)
        logger.info(f"Download activity {activity['activityId']} from Garmin CN done!")

        logger.info(f"Upload activity {activity['activityId']} to Garmin Global ...")
        client.upload_activity(activity_file)
        logger.info(f"Upload activity {activity['activityId']} to Garmin Global done!")
    except Exception as e:
        if "Conflict for url" in str(e):
            logger.info("Upload fail, the activity probably already exists.")
            continue
    finally:
        os.remove(activity_file)
