"""
API Client for communicating with the backend Node.js server
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import logging

class APIClient:
    """Python client for HTTP requests to the Node.js backend"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MultiAPI-Drive-Manager/1.0'
        })
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Connection timeout
        self.timeout = 10
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to the API"""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            
            # Log request
            self.logger.info(f"{method} {endpoint} - Status: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Check backend health status"""
        return self._make_request('GET', '/health')
    
    # Account Management
    def start_oauth(self) -> Dict[str, Any]:
        """Start OAuth flow"""
        return self._make_request('POST', '/accounts/oauth/start')
    
    def get_accounts(self) -> Dict[str, Any]:
        """Get all accounts"""
        return self._make_request('GET', '/accounts')
    
    def get_account(self, account_key: str) -> Dict[str, Any]:
        """Get account by key"""
        return self._make_request('GET', f'/accounts/{account_key}')
    
    def delete_account(self, account_key: str) -> Dict[str, Any]:
        """Delete account"""
        return self._make_request('DELETE', f'/accounts/{account_key}')
    
    def get_account_status(self, account_key: str) -> Dict[str, Any]:
        """Get account sync status"""
        return self._make_request('GET', f'/accounts/{account_key}/status')
    
    def register_service_account(self, alias: str, private_key: str, root_folder_ids: List[str]) -> Dict[str, Any]:
        """Register a service account"""
        data = {
            'alias': alias,
            'privateKey': private_key,
            'rootFolderIds': root_folder_ids
        }
        return self._make_request('POST', '/accounts/sa', json=data)
    
    # Sync Operations
    def start_initial_crawl(self, account_key: str) -> Dict[str, Any]:
        """Start initial crawl for an account"""
        return self._make_request('POST', f'/sync/{account_key}/initial')
    
    def start_incremental_sync(self, account_key: str) -> Dict[str, Any]:
        """Start incremental sync for an account"""
        return self._make_request('POST', f'/sync/{account_key}/incremental')
    
    def get_sync_status(self, account_key: str) -> Dict[str, Any]:
        """Get sync status for an account"""
        return self._make_request('GET', f'/sync/{account_key}/status')
    
    # Search Operations
    def search_files(self, query: str = '', **filters) -> Dict[str, Any]:
        """Search files with filters"""
        params = {'q': query}
        params.update(filters)
        return self._make_request('GET', '/search', params=params)
    
    # Upload Operations
    def upload_file(self, account_key: str, file_path: str, parent_id: str = None) -> Dict[str, Any]:
        """Upload file to Google Drive"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'accountKey': account_key,
                    'parentId': parent_id
                }
                url = f"{self.base_url}/files/upload/multipart"
                response = self.session.post(url, files=files, data=data, timeout=300)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_upload_url(self, account_key: str, file_name: str, mime_type: str = None, 
                      parent_id: str = None, file_size: int = None) -> Dict[str, Any]:
        """Get upload URL for file"""
        data = {
            'accountKey': account_key,
            'fileName': file_name,
            'mimeType': mime_type,
            'parentId': parent_id,
            'fileSize': file_size
        }
        return self._make_request('POST', '/files/upload', json=data)
    
    def complete_upload(self, file_id: str, account_key: str) -> Dict[str, Any]:
        """Complete file upload"""
        data = {'accountKey': account_key}
        return self._make_request('POST', f'/files/upload/{file_id}/complete', json=data)
    
    def export_search_results(self, query: str = '', format: str = 'csv', fields: str = '', **filters) -> Dict[str, Any]:
        """Export search results"""
        params = {
            'q': query,
            'format': format,
            'fields': fields
        }
        params.update(filters)
        return self._make_request('GET', '/search/export', params=params)
    
    def get_files_for_account(self, account_key: str, **filters) -> Dict[str, Any]:
        """Get files for a specific account"""
        params = {'owner': account_key}
        params.update(filters)
        return self._make_request('GET', '/search', params=params)
    
    def advanced_search(self, queries: List[Dict], filters: Dict = None, sort: Dict = None, pagination: Dict = None) -> Dict[str, Any]:
        """Advanced search with complex criteria"""
        data = {
            'queries': queries or [],
            'filters': filters or {},
            'sort': sort or {},
            'pagination': pagination or {}
        }
        return self._make_request('POST', '/search/advanced', json=data)
    
    def get_search_suggestions(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Get search suggestions"""
        params = {'q': query, 'limit': limit}
        return self._make_request('GET', '/search/suggestions', params=params)
    
    def get_search_stats(self, owner: str = '') -> Dict[str, Any]:
        """Get search statistics"""
        params = {'owner': owner} if owner else {}
        return self._make_request('GET', '/search/stats', params=params)
    
    # File Operations
    def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata"""
        return self._make_request('GET', f'/files/{file_id}')
    
    def get_file_path(self, file_id: str) -> Dict[str, Any]:
        """Get file virtual path"""
        return self._make_request('GET', f'/files/{file_id}/path')
    
    def get_file_siblings(self, file_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get files in same folder"""
        params = {'limit': limit}
        return self._make_request('GET', f'/files/{file_id}/siblings', params=params)
    
    def get_file_sharing(self, file_id: str) -> Dict[str, Any]:
        """Get file sharing information"""
        return self._make_request('GET', f'/files/{file_id}/sharing')
    
    def get_file_preview(self, file_id: str) -> Dict[str, Any]:
        """Get file preview information"""
        return self._make_request('GET', f'/files/{file_id}/preview')
    
    def download_file(self, file_id: str, format: str = None) -> Dict[str, Any]:
        """Legacy method (JSON). Not suitable for binary downloads."""
        params = {}
        if format:
            params['format'] = format
        return self._make_request('GET', f'/files/{file_id}/download', params=params)

    def download_file_raw(self, file_id: str, format: Optional[str] = None):
        """Request file download as raw streamed response (no JSON parsing)."""
        url = urljoin(self.base_url, f'/files/{file_id}/download')
        params = {}
        if format:
            params['format'] = format
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout, stream=True)
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Download request failed: {e}")
            raise

    def download_file_to_path(self, file_id: str, dest_path: str, format: Optional[str] = None, chunk_size: int = 1024 * 1024):
        """Stream download to a file on disk. Returns saved path."""
        resp = self.download_file_raw(file_id, format)
        total = resp.headers.get('Content-Length')
        with open(dest_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        return dest_path
    
    def bulk_operations(self, file_ids: List[str], operation: str, destination_folder_id: str = None) -> Dict[str, Any]:
        """Perform bulk operations on files"""
        data = {
            'fileIds': file_ids,
            'operation': operation
        }
        if destination_folder_id:
            data['destinationFolderId'] = destination_folder_id
        return self._make_request('POST', '/files/bulk', json=data)
    
    def export_search_results(self, query: str = '', format: str = 'csv', fields: str = None, **filters) -> Dict[str, Any]:
        """Export search results"""
        data = {
            'q': query,
            'format': format,
            'fields': fields or 'name,mime_type,size,modified_time,account_key'
        }
        data.update(filters)
        return self._make_request('POST', '/search/export', json=data)
    
    def get_bulk_files(self, file_ids: List[str]) -> Dict[str, Any]:
        """Get multiple files metadata"""
        data = {'fileIds': file_ids}
        return self._make_request('POST', '/files/bulk', json=data)
    
    # Reports
    def get_dedup_report(self, min_size: int = 0, group_by: str = 'md5', limit: int = 100) -> Dict[str, Any]:
        """Get duplicate files report"""
        params = {
            'minSize': min_size,
            'groupBy': group_by,
            'limit': limit
        }
        return self._make_request('GET', '/reports/dedup', params=params)
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get system health report"""
        return self._make_request('GET', '/reports/health')
    
    def get_storage_report(self, account_key: str = '') -> Dict[str, Any]:
        """Get storage analysis report"""
        params = {'accountKey': account_key} if account_key else {}
        return self._make_request('GET', '/reports/storage', params=params)
    
    def get_sync_performance_report(self) -> Dict[str, Any]:
        """Get sync performance report"""
        return self._make_request('GET', '/reports/sync-performance')
    
    # Utility methods
    def is_connected(self) -> bool:
        """Check if backend is connected"""
        try:
            response = self.health_check()
            return response.get('success', False)
        except:
            return False
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information"""
        try:
            response = self.health_check()
            if response.get('success'):
                return {
                    'connected': True,
                    'version': response.get('version'),
                    'environment': response.get('environment'),
                    'timestamp': response.get('timestamp')
                }
            else:
                return {'connected': False}
        except:
            return {'connected': False}
    
    def close(self):
        """Close the API client session"""
        self.session.close()
