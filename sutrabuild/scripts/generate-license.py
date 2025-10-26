#!/usr/bin/env python3
"""
Sutra AI License Generator

Generates HMAC-signed license keys for Community and Enterprise editions.

Usage:
    python scripts/generate-license.py --edition community --customer "Acme Corp" --days 365
    
License format:
    base64(json({edition, expires, customer_id, issued})).hmac_signature
"""

import os
import sys
import argparse
import hashlib
import hmac
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.feature_flags import Edition


def generate_license(
    edition: str,
    customer_id: str,
    days: int,
    secret_key: str
) -> str:
    """
    Generate a signed license key
    
    Args:
        edition: simple, community, or enterprise
        customer_id: Customer identifier
        days: License validity in days (0 = permanent)
        secret_key: HMAC secret key
        
    Returns:
        Signed license key string
    """
    # Validate edition
    try:
        ed = Edition(edition.lower())
    except ValueError:
        raise ValueError(f"Invalid edition: {edition}. Must be: simple, community, enterprise")
    
    # Create license data
    license_data = {
        "edition": ed.value,
        "customer_id": customer_id,
        "issued": datetime.now().isoformat(),
    }
    
    # Add expiration if not permanent
    if days > 0:
        expires = datetime.now() + timedelta(days=days)
        license_data["expires"] = expires.isoformat()
    else:
        license_data["expires"] = None  # Permanent license
    
    # Encode license data
    license_json = json.dumps(license_data, separators=(',', ':'))
    license_b64 = base64.b64encode(license_json.encode()).decode()
    
    # Generate HMAC signature
    signature = hmac.new(
        secret_key.encode(),
        license_b64.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Combine: base64_data.signature
    license_key = f"{license_b64}.{signature}"
    
    return license_key, license_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate Sutra AI license keys",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Community license for 1 year
  python scripts/generate-license.py --edition community --customer "Acme Corp" --days 365
  
  # Enterprise permanent license
  python scripts/generate-license.py --edition enterprise --customer "BigCo Inc" --days 0
  
  # Use custom secret key
  export SUTRA_LICENSE_SECRET="your-secret-key-here"
  python scripts/generate-license.py --edition community --customer "Test Co" --days 30
"""
    )
    
    parser.add_argument(
        "--edition",
        required=True,
        choices=["community", "enterprise"],
        help="License edition (simple is always free)"
    )
    
    parser.add_argument(
        "--customer",
        required=True,
        help="Customer name or ID"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="License validity in days (0 = permanent, default: 365)"
    )
    
    parser.add_argument(
        "--secret",
        default=None,
        help="HMAC secret key (default: SUTRA_LICENSE_SECRET env var)"
    )
    
    args = parser.parse_args()
    
    # Get secret key
    secret_key = args.secret or os.getenv("SUTRA_LICENSE_SECRET")
    if not secret_key:
        print("ERROR: SUTRA_LICENSE_SECRET environment variable not set")
        print()
        print("Set a strong secret key:")
        print("  export SUTRA_LICENSE_SECRET=\"$(openssl rand -hex 32)\"")
        sys.exit(1)
    
    # Generate license
    try:
        license_key, license_data = generate_license(
            edition=args.edition,
            customer_id=args.customer,
            days=args.days,
            secret_key=secret_key
        )
        
        # Print license details
        print("=" * 80)
        print(f"Sutra AI {args.edition.upper()} License Generated")
        print("=" * 80)
        print()
        print(f"Customer:    {license_data['customer_id']}")
        print(f"Edition:     {license_data['edition']}")
        print(f"Issued:      {license_data['issued']}")
        
        if license_data['expires']:
            print(f"Expires:     {license_data['expires']}")
        else:
            print(f"Expires:     Never (permanent)")
        
        print()
        print("License Key:")
        print("-" * 80)
        print(license_key)
        print("-" * 80)
        print()
        print("Deployment:")
        print(f"  export SUTRA_EDITION=\"{args.edition}\"")
        print(f"  export SUTRA_LICENSE_KEY=\"{license_key}\"")
        print(f"  ./sutra-deploy.sh install")
        print()
        print("=" * 80)
        
        # Save to file
        output_file = f"license-{args.customer.replace(' ', '-').lower()}-{args.edition}.txt"
        with open(output_file, "w") as f:
            f.write(f"Sutra AI {args.edition.upper()} License\n")
            f.write(f"Customer: {license_data['customer_id']}\n")
            f.write(f"Issued: {license_data['issued']}\n")
            f.write(f"Expires: {license_data['expires'] or 'Never'}\n")
            f.write(f"\n")
            f.write(f"License Key:\n")
            f.write(f"{license_key}\n")
            f.write(f"\n")
            f.write(f"Deployment:\n")
            f.write(f"  export SUTRA_EDITION=\"{args.edition}\"\n")
            f.write(f"  export SUTRA_LICENSE_KEY=\"{license_key}\"\n")
            f.write(f"  ./sutra-deploy.sh install\n")
        
        print(f"License saved to: {output_file}")
        print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
