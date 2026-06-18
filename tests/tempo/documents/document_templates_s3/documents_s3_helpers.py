"""S3-specific helper for the document-templates-s3 migration (VCITA2-14225).

The upload / list / grab-link / client-access flow is shared with the sibling
`document_templates` (authenticated) migration and is reused from
`tests.tempo.documents.document_templates.documents_helpers`.

The only behavioral distinction of the s3 feature is the storage backend: with the
AWS-S3 documents backend (the default on integration), the grabbed public document link
carries a `fileStorageType=AWS-S3` query parameter. Verified live:
`.../uploads/documents/<id>/clientDoc.pdf?fileStorageType=AWS-S3`.
"""

S3_STORAGE_SIGNAL = "fileStorageType=AWS-S3"


def assert_link_is_s3(link: str) -> None:
    """Assert the grabbed public document link is served from the AWS-S3 backend
    (legacy s3 feature's defining distinction vs the authenticated backend)."""
    if S3_STORAGE_SIGNAL not in link:
        raise AssertionError(
            f"Grabbed document link is not served from the AWS-S3 backend "
            f"(expected {S3_STORAGE_SIGNAL!r} in the link): {link!r}"
        )
