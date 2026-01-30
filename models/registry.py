from models.profiles import MODEL_PROFILES, ModelProfile


def list_profiles():
    return list(MODEL_PROFILES.values())


def get_profile(profile_id: str) -> ModelProfile:
    if profile_id not in MODEL_PROFILES:
        raise KeyError(f"Unknown model profile: {profile_id}")
    return MODEL_PROFILES[profile_id]
