"""
Comprehensive tests for file upload functionality
Tests various file types: images, videos, documents, executables, and archives
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import base64
import io


# Use the app's client
client = TestClient(app)


@pytest.fixture
def workspace(db_session):
    """Create a test workspace"""
    response = client.post(
        "/workspaces",
        json={"name": "Test Workspace", "description": "For file upload tests"}
    )
    assert response.status_code == 201
    return response.json()


class TestImageUpload:
    """Test uploading image files (PNG, JPG, GIF, etc.)"""
    
    def test_upload_png_image(self, workspace, db_session):
        """Test uploading a PNG image"""
        workspace_id = workspace["id"]
        
        # Create a simple PNG image (minimal valid PNG)
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("test_image.png", io.BytesIO(png_data), "image/png")},
            data={"description": "Test PNG image"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_image.png"
        assert data["asset_type"] == "image"
        assert data["mime_type"] == "image/png"
        assert data["file_size"] == len(png_data)
        assert data["description"] == "Test PNG image"
    
    def test_upload_jpg_image(self, workspace, db_session):
        """Test uploading a JPG image"""
        workspace_id = workspace["id"]
        
        # Simple JPG data (minimal valid JPEG header)
        jpg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("photo.jpg", io.BytesIO(jpg_data), "image/jpeg")},
            data={"description": "Test JPG photo"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "image"
        assert data["mime_type"] == "image/jpeg"


class TestVideoUpload:
    """Test uploading video files (MP4, AVI, MOV, etc.)"""
    
    def test_upload_mp4_video(self, workspace, db_session):
        """Test uploading an MP4 video"""
        workspace_id = workspace["id"]
        video_data = b"\x00\x00\x00\x18ftypmp42"  # Minimal MP4 header
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("video.mp4", io.BytesIO(video_data), "video/mp4")},
            data={"description": "Test video"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "video"
        assert data["mime_type"] == "video/mp4"
        assert data["file_size"] == len(video_data)
    
    def test_upload_webm_video(self, workspace, db_session):
        """Test uploading a WEBM video"""
        workspace_id = workspace["id"]
        video_data = b"\x1aE\xdf\xa3"  # WEBM signature
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("video.webm", io.BytesIO(video_data), "video/webm")},
            data={"description": "WebM format video"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "video"
        assert data["mime_type"] == "video/webm"


class TestDocumentUpload:
    """Test uploading document files (PDF, DOCX, XLSX, TXT, etc.)"""
    
    def test_upload_pdf_document(self, workspace, db_session):
        """Test uploading a PDF document"""
        workspace_id = workspace["id"]
        pdf_data = b"%PDF-1.4\n%fake pdf content"
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("document.pdf", io.BytesIO(pdf_data), "application/pdf")},
            data={"description": "Test PDF document"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "document"
        assert data["mime_type"] == "application/pdf"
        assert data["name"] == "document.pdf"
    
    def test_upload_txt_document(self, workspace, db_session):
        """Test uploading a TXT file"""
        workspace_id = workspace["id"]
        txt_data = b"This is a plain text document.\nWith multiple lines."
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("notes.txt", io.BytesIO(txt_data), "text/plain")},
            data={"description": "Text notes"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "document"
        assert data["mime_type"] == "text/plain"
    
    def test_upload_csv_document(self, workspace, db_session):
        """Test uploading a CSV file"""
        workspace_id = workspace["id"]
        csv_data = b"Name,Age,City\nAlice,30,NYC\nBob,25,LA"
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("data.csv", io.BytesIO(csv_data), "text/csv")},
            data={"description": "CSV data"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "document"
        assert data["mime_type"] == "text/csv"


class TestExecutableUpload:
    """Test uploading executable and script files"""
    
    def test_upload_exe_executable(self, workspace, db_session):
        """Test uploading an EXE executable"""
        workspace_id = workspace["id"]
        exe_data = b"MZ\x90\x00"  # EXE header
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("app.exe", io.BytesIO(exe_data), "application/x-msdownload")},
            data={"description": "Windows executable"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "executable"
        assert data["mime_type"] == "application/x-msdownload"
    
    def test_upload_python_script(self, workspace, db_session):
        """Test uploading a Python script"""
        workspace_id = workspace["id"]
        py_data = b"#!/usr/bin/env python3\nprint('Hello, World!')"
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("script.py", io.BytesIO(py_data), "text/x-python")},
            data={"description": "Python script"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "code"
        assert data["file_size"] == len(py_data)


class TestArchiveUpload:
    """Test uploading archive files"""
    
    def test_upload_zip_archive(self, workspace, db_session):
        """Test uploading a ZIP archive"""
        workspace_id = workspace["id"]
        zip_data = b"PK\x03\x04"  # ZIP file signature
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("archive.zip", io.BytesIO(zip_data), "application/zip")},
            data={"description": "ZIP archive"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "archive"
        assert data["mime_type"] == "application/zip"
    
    def test_upload_tar_gz_archive(self, workspace, db_session):
        """Test uploading a TAR.GZ archive"""
        workspace_id = workspace["id"]
        targz_data = b"\x1f\x8b\x08"  # GZIP header
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("files.tar.gz", io.BytesIO(targz_data), "application/gzip")},
            data={"description": "Compressed archive"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["asset_type"] == "archive"
        assert data["mime_type"] == "application/gzip"


class TestFileOperations:
    """Test file upload/download/list operations"""
    
    def test_upload_and_list_files(self, workspace, db_session):
        """Test uploading multiple files and listing them"""
        workspace_id = workspace["id"]
        
        # Upload first file
        response1 = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("file1.txt", io.BytesIO(b"Content 1"), "text/plain")},
        )
        assert response1.status_code == 201
        
        # Upload second file
        response2 = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("file2.txt", io.BytesIO(b"Content 2"), "text/plain")},
        )
        assert response2.status_code == 201
        
        # List all files in workspace
        list_response = client.get(f"/assets/{workspace_id}")
        assert list_response.status_code == 200
        assets = list_response.json()
        assert len(assets) == 2
        assert assets[0]["name"] == "file1.txt"
        assert assets[1]["name"] == "file2.txt"
    
    def test_download_uploaded_file(self, workspace, db_session):
        """Test downloading an uploaded file"""
        workspace_id = workspace["id"]
        
        # Upload a file
        file_content = b"Test file content"
        upload_response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
        )
        assert upload_response.status_code == 201
        asset_id = upload_response.json()["id"]
        
        # Download the file
        download_response = client.get(f"/assets/asset/{asset_id}/download")
        assert download_response.status_code == 200
        assert download_response.content == file_content
        assert "text/plain" in download_response.headers["content-type"]
    
    def test_get_file_metadata(self, workspace, db_session):
        """Test retrieving file metadata without downloading"""
        workspace_id = workspace["id"]
        file_content = b"Metadata test content"
        
        # Upload file
        upload_response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("metadata.txt", io.BytesIO(file_content), "text/plain")},
            data={"description": "Test metadata"}
        )
        assert upload_response.status_code == 201
        asset_id = upload_response.json()["id"]
        
        # Get metadata
        metadata_response = client.get(f"/assets/asset/{asset_id}")
        assert metadata_response.status_code == 200
        metadata = metadata_response.json()
        assert metadata["file_size"] == len(file_content)
        assert metadata["mime_type"] == "text/plain"
        assert metadata["description"] == "Test metadata"
        assert metadata["asset_type"] == "document"


class TestErrorHandling:
    """Test error handling in file uploads"""
    
    def test_upload_to_nonexistent_workspace(self, db_session):
        """Test uploading to a workspace that doesn't exist"""
        response = client.post(
            f"/assets/nonexistent-id/upload",
            files={"file": ("test.txt", io.BytesIO(b"test"), "text/plain")},
        )
        assert response.status_code == 404
        assert "Workspace not found" in response.json()["detail"]
    
    def test_download_nonexistent_file(self, db_session):
        """Test downloading a file that doesn't exist"""
        response = client.get("/assets/asset/nonexistent-id/download")
        assert response.status_code == 404
        assert "Asset not found" in response.json()["detail"]
    
    def test_get_nonexistent_file_metadata(self, db_session):
        """Test getting metadata for non-existent file"""
        response = client.get("/assets/asset/nonexistent-id")
        assert response.status_code == 404
        assert "Asset not found" in response.json()["detail"]
    
    def test_upload_without_file(self, workspace, db_session):
        """Test upload endpoint without providing file"""
        workspace_id = workspace["id"]
        response = client.post(f"/assets/{workspace_id}/upload")
        assert response.status_code == 422  # Validation error


class TestLargeFiles:
    """Test handling of large files"""
    
    def test_upload_large_binary_file(self, workspace, db_session):
        """Test uploading a large binary file"""
        workspace_id = workspace["id"]
        # Create 1MB of data
        large_data = b"\x00" * (1024 * 1024)
        
        response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("large.bin", io.BytesIO(large_data), "application/octet-stream")},
            data={"description": "Large binary file"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["file_size"] == len(large_data)


class TestMimeTypeDetection:
    """Test MIME type detection and asset type classification"""
    
    def test_mime_type_detection_various_formats(self, workspace, db_session):
        """Test MIME type detection for various file formats"""
        workspace_id = workspace["id"]
        
        test_cases = [
            ("image.gif", b"GIF89a", "image/gif", "image"),
            ("audio.mp3", b"ID3", "audio/mpeg", "audio"),
            ("code.js", b"console.log('test');", "text/javascript", "code"),
            ("data.json", b'{"key": "value"}', "application/json", "file"),
        ]
        
        for filename, content, mime_type, expected_type in test_cases:
            response = client.post(
                f"/assets/{workspace_id}/upload",
                files={"file": (filename, io.BytesIO(content), mime_type)},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["mime_type"] == mime_type
            assert data["asset_type"] in [expected_type, "file"]


class TestFileIntegration:
    """Integration tests for file uploads with other features"""
    
    def test_upload_and_add_to_kit(self, workspace, db_session):
        """Test uploading files and adding them to a kit"""
        workspace_id = workspace["id"]
        
        # Upload a file
        upload_response = client.post(
            f"/assets/{workspace_id}/upload",
            files={"file": ("integration.txt", io.BytesIO(b"Integration test"), "text/plain")},
        )
        assert upload_response.status_code == 201
        asset_id = upload_response.json()["id"]
        
        # Create a kit with the uploaded asset
        kit_response = client.post(
            f"/kits/{workspace_id}",
            json={"name": "Test Kit", "asset_ids": [asset_id]}
        )
        assert kit_response.status_code == 201
        kit_data = kit_response.json()
        
        # Verify asset is in kit
        assert len(kit_data["assets"]) == 1
        assert kit_data["assets"][0]["id"] == asset_id
    
    def test_multiple_file_uploads_different_types(self, workspace, db_session):
        """Test uploading different file types to same workspace"""
        workspace_id = workspace["id"]
        
        files_to_upload = [
            ("image.png", b"\x89PNG\r\n\x1a\n", "image/png", "image"),
            ("video.mp4", b"\x00\x00\x00\x18ftyp", "video/mp4", "video"),
            ("document.pdf", b"%PDF-1.4", "application/pdf", "document"),
            ("script.py", b"print('hello')", "text/x-python", "code"),
        ]
        
        asset_ids = []
        for filename, content, mime_type, expected_type in files_to_upload:
            response = client.post(
                f"/assets/{workspace_id}/upload",
                files={"file": (filename, io.BytesIO(content), mime_type)},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["asset_type"] == expected_type
            asset_ids.append(data["id"])
        
        # Verify all files are in the workspace
        list_response = client.get(f"/assets/{workspace_id}")
        assert list_response.status_code == 200
        assets = list_response.json()
        assert len(assets) == 4
