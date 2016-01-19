from app import FREE_EMAILS_SET


def transform_email_if_useful(email, user_id):
    """ Helper which transform original email to: user_id@email_domain.com
    If it is useful (e.g. non-free).
    """
    email_domain = (email or '').split('@')[-1].strip()

    if not email_domain or email_domain in FREE_EMAILS_SET:
        return None

    return '{}@{}'.format(user_id, email_domain)
