
import ipaddress
import math
import re
from collections import Counter
from urllib.parse import urlsplit


# We will initially train the corrected model using 14 reproducible features.
# token_count and tld_popularity are excluded because their original
# dataset calculation methods have not yet been established.
FEATURE_COLUMNS = [
    "url_length",
    "has_ip_address",
    "dot_count",
    "https_flag",
    "url_entropy",
    "subdomain_count",
    "query_param_count",
    "tld_length",
    "path_length",
    "has_hyphen_in_domain",
    "number_of_digits",
    "suspicious_file_extension",
    "domain_name_length",
    "percentage_numeric_chars",
]


SUSPICIOUS_EXTENSIONS = {
    ".exe",
    ".zip",
    ".rar",
    ".scr",
    ".bat",
    ".cmd",
    ".msi",
    ".apk",
    ".jar",
    ".dll",
}


def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0

    counts = Counter(text)
    length = len(text)

    return -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )


def extract_features(url: str) -> dict:
    """
    Extract the 14 selected numerical features from a URL.

    Note:
    The extraction logic for query_param_count has been verified against
    the original dataset. Exact parity for every other feature has not
    yet been established.
    """
    if not isinstance(url, str):
        raise ValueError("URL must be a string.")

    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    # Add a scheme when the user enters a bare domain.
    normalized_url = (
        url if "://" in url else f"http://{url}"
    )

    parsed = urlsplit(normalized_url)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""

    # 1. URL length
    url_length = len(url)

    # 2. Check whether the hostname is an IP address.
    has_ip_address = 0

    try:
        if hostname:
            ipaddress.ip_address(hostname)
            has_ip_address = 1
    except ValueError:
        pass

    # 3. Count dots in the original URL.
    dot_count = url.count(".")

    # 4. HTTPS flag
    https_flag = int(parsed.scheme.lower() == "https")

    # 5. Shannon entropy
    url_entropy = calculate_entropy(url)

    # Split hostname into labels.
    labels = hostname.split(".") if hostname else []
    tld = labels[-1] if labels else ""

    # Approximate the main domain label.
    domain_name = (
        labels[-2] if len(labels) >= 2
        else labels[0] if labels
        else ""
    )

    # 6. Approximate subdomain count.
    subdomain_count = (
        max(0, len(labels) - 2) if labels else 0
    )

    # 7. Query parameter count.
    # This formula matched query_param_count across all 101,219
    # original dataset rows during our validation.
    query = parsed.query
    query_param_count = (
        max(1, len(query.split("&"))) if query else 1
    )

    # 8. TLD length
    tld_length = len(tld)

    # 9. URL path length
    path_length = len(path)

    # 10. Whether the hostname contains a hyphen.
    has_hyphen_in_domain = int("-" in hostname)

    # 11. Count numeric characters in the original URL.
    number_of_digits = sum(char.isdigit() for char in url)

    # 12. Flag suspicious file extensions in the URL path.
    path_lower = path.lower()

    suspicious_file_extension = int(
        any(
            path_lower.endswith(extension)
            for extension in SUSPICIOUS_EXTENSIONS
        )
    )

    # 13. Main domain label length.
    domain_name_length = len(domain_name)

    # 14. Percentage of URL characters that are numeric.
    percentage_numeric_chars = (
        number_of_digits / len(url) * 100
    )

    features = {
        "url_length": url_length,
        "has_ip_address": has_ip_address,
        "dot_count": dot_count,
        "https_flag": https_flag,
        "url_entropy": url_entropy,
        "subdomain_count": subdomain_count,
        "query_param_count": query_param_count,
        "tld_length": tld_length,
        "path_length": path_length,
        "has_hyphen_in_domain": has_hyphen_in_domain,
        "number_of_digits": number_of_digits,
        "suspicious_file_extension": suspicious_file_extension,
        "domain_name_length": domain_name_length,
        "percentage_numeric_chars": percentage_numeric_chars,
    }

    return features
