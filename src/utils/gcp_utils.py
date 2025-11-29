"""
Google Cloud Platform integration utilities
Supports Cloud Storage, Secret Manager, and Cloud SQL
"""

import os
from typing import Optional


def get_gcp_project_id() -> Optional[str]:
    """Get GCP project ID from environment or metadata server"""
    project_id = os.getenv('GCP_PROJECT_ID')
    
    if not project_id:
        try:
            # Try to get from GCP metadata server (when running on GCP)
            import requests
            metadata_server = "http://metadata.google.internal/computeMetadata/v1/"
            metadata_flavor = {'Metadata-Flavor': 'Google'}
            project_id = requests.get(
                metadata_server + 'project/project-id',
                headers=metadata_flavor,
                timeout=1
            ).text
        except:
            pass
    
    return project_id


class CloudStorageManager:
    """Manage file storage in Google Cloud Storage"""
    
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv('GCP_BUCKET_NAME')
        self.client = None
        self.bucket = None
        
        if self.bucket_name:
            try:
                from google.cloud import storage
                self.client = storage.Client()
                self.bucket = self.client.bucket(self.bucket_name)
            except Exception as e:
                print(f"Warning: Could not initialize Cloud Storage: {e}")
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to Cloud Storage"""
        if not self.bucket:
            return False
        
        try:
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            return True
        except Exception as e:
            print(f"Error uploading to Cloud Storage: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download a file from Cloud Storage"""
        if not self.bucket:
            return False
        
        try:
            blob = self.bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            return True
        except Exception as e:
            print(f"Error downloading from Cloud Storage: {e}")
            return False
    
    def list_files(self, prefix: str = '') -> list:
        """List files in the bucket with optional prefix"""
        if not self.bucket:
            return []
        
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"Error listing Cloud Storage files: {e}")
            return []
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from Cloud Storage"""
        if not self.bucket:
            return False
        
        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting from Cloud Storage: {e}")
            return False


class SecretManager:
    """Manage secrets using Google Cloud Secret Manager"""
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or get_gcp_project_id()
        self.client = None
        
        if self.project_id:
            try:
                from google.cloud import secretmanager
                self.client = secretmanager.SecretManagerServiceClient()
            except Exception as e:
                print(f"Warning: Could not initialize Secret Manager: {e}")
    
    def get_secret(self, secret_id: str, version: str = 'latest') -> Optional[str]:
        """Retrieve a secret from Secret Manager"""
        if not self.client:
            return None
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode('UTF-8')
        except Exception as e:
            print(f"Error accessing secret: {e}")
            return None
    
    def create_secret(self, secret_id: str, secret_value: str) -> bool:
        """Create a new secret in Secret Manager"""
        if not self.client:
            return False
        
        try:
            parent = f"projects/{self.project_id}"
            
            # Create the secret
            secret = self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
            
            # Add the secret version
            self.client.add_secret_version(
                request={
                    "parent": secret.name,
                    "payload": {"data": secret_value.encode('UTF-8')},
                }
            )
            return True
        except Exception as e:
            print(f"Error creating secret: {e}")
            return False


def get_database_url() -> str:
    """
    Get database URL with Cloud SQL support
    
    For Cloud SQL, use Unix socket connection:
    postgresql://user:password@/dbname?host=/cloudsql/project:region:instance
    """
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        # Check for Cloud SQL connection
        cloud_sql_connection = os.getenv('CLOUD_SQL_CONNECTION_NAME')
        if cloud_sql_connection:
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', '')
            db_name = os.getenv('DB_NAME', 'etf_analysis')
            
            # Use Secret Manager for password if available
            if not db_password:
                sm = SecretManager()
                db_password = sm.get_secret('db-password') or ''
            
            db_url = f"postgresql://{db_user}:{db_password}@/{db_name}?host=/cloudsql/{cloud_sql_connection}"
        else:
            # Default to SQLite for local development
            db_url = 'sqlite:///./data/etf_analysis.db'
    
    return db_url


# Example usage in Streamlit app
def configure_gcp_integration():
    """
    Configure GCP services for the application
    Call this at app startup
    """
    project_id = get_gcp_project_id()
    
    if project_id:
        print(f"Running on GCP Project: {project_id}")
        
        # Initialize services
        storage = CloudStorageManager()
        secrets = SecretManager()
        
        return {
            'project_id': project_id,
            'storage': storage,
            'secrets': secrets,
            'database_url': get_database_url()
        }
    else:
        print("Running locally without GCP integration")
        return {
            'project_id': None,
            'storage': None,
            'secrets': None,
            'database_url': 'sqlite:///./data/etf_analysis.db'
        }
