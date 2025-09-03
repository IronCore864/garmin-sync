import logging
import os

from garminconnect import Garmin
import zipfile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


cn_client = Garmin(
    os.environ.get("GARMIN_CN_EMAIL"),
    os.environ.get("GARMIN_CN_PASSWORD"),
    is_cn=True,
)
cn_client.login()
logger.info("Garmin CN login successful!")
cn_client.garth.configure(timeout=30, retries=3)

activities_num = 3
logger.info(f"Get latest {activities_num} activities from Garmin CN ...")
activities = cn_client.get_activities(0, activities_num)
logger.info(f"Get latest {activities_num} activities from Garmin CN done!")

logger.info("Login to Garmin Global ...")
client = Garmin(
    os.environ.get("GARMIN_GLOBAL_EMAIL"), os.environ.get("GARMIN_GLOBAL_PASSWORD")
)
client.login()
logger.info("Garmin Global login successful!")

for activity in activities:
    activity_file = f"./{activity["activityId"]}.zip"
    try:
        logger.info(
            f"Activity {activity['activityId']}: {activity['activityName']}, started on {activity['startTimeLocal']}"
        )
        logger.info(f"Download activity {activity['activityId']} from Garmin CN ...")
        activity_bytes = cn_client.download_activity(activity["activityId"], dl_fmt=Garmin.ActivityDownloadFormat.ORIGINAL)
        with open(activity_file, "wb") as f:
            f.write(activity_bytes)
        logger.info(f"Download activity {activity['activityId']} from Garmin CN done!")

        with zipfile.ZipFile(activity_file, "r") as z:
            z.extractall(f"./{activity['activityId']}")
            unzipped_files = z.namelist()
        logger.info(f"Upload activity {activity['activityId']}/{unzipped_files[0]} to Garmin Global ...")
        client.upload_activity(f"./{activity['activityId']}/{unzipped_files[0]}")
        logger.info(f"Upload activity {activity['activityId']} to Garmin Global done!")
    except Exception as e:
        if "Conflict for url" in str(e):
            logger.info("Upload fail, the activity probably already exists.")
            continue
        logger.info(e)
    finally:
        if os.path.exists(activity_file):
            os.remove(activity_file)
        for f in unzipped_files:
            os.remove(f"./{activity['activityId']}/{f}")
        os.rmdir(f"./{activity['activityId']}")
