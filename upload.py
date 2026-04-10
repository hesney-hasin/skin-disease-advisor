from huggingface_hub import HfApi

api = HfApi()
api.upload_folder(
    folder_path="D:/skin-disease-advisor/skin-disease-advisor",
    repo_id="hesneyhasin/skin-disease-advisor",
    repo_type="space"
)