from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """測試根路徑重定向到靜態文件"""
    # Arrange - 設置測試環境（這裡不需要特別設置）
    
    # Act - 執行動作
    response = client.get("/", follow_redirects=False)
    
    # Assert - 驗證結果
    assert response.status_code == 307
    assert "/static/index.html" in response.headers.get("location", "")

def test_get_activities():
    """測試獲取所有活動"""
    # Arrange - 設置測試環境（數據已由 conftest.py 重置）
    
    # Act - 執行動作
    response = client.get("/activities")
    
    # Assert - 驗證結果
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 7  # 應該有 7 個活動
    
    # 檢查每個活動的結構
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)

def test_signup_success():
    """測試成功報名活動"""
    # Arrange - 準備測試數據
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # Act - 執行報名動作
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert - 驗證報名成功
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    
    # 驗證參與者已被添加到活動中
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """測試重複報名同一活動"""
    # Arrange - 準備測試數據並先報名一次
    email = "test@mergington.edu"
    activity_name = "Programming Class"
    client.post(f"/activities/{activity_name}/signup?email={email}")  # 先報名
    
    # Act - 嘗試再次報名
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert - 驗證重複報名被拒絕
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_activity_not_found():
    """測試報名不存在的活動"""
    # Arrange - 準備測試數據
    email = "test@mergington.edu"
    invalid_activity = "Nonexistent Activity"
    
    # Act - 嘗試報名不存在的活動
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert - 驗證返回 404 錯誤
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    """測試成功取消報名"""
    # Arrange - 準備測試數據並先報名
    email = "removeme@mergington.edu"
    activity_name = "Gym Class"
    client.post(f"/activities/{activity_name}/signup?email={email}")  # 先報名
    
    # Act - 執行取消報名動作
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert - 驗證取消報名成功
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # 驗證參與者已被從活動中移除
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """測試取消報名未報名的學生"""
    # Arrange - 準備測試數據
    email = "notregistered@mergington.edu"
    activity_name = "Art Workshop"
    
    # Act - 嘗試取消未報名的學生
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert - 驗證返回 400 錯誤
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]

def test_unregister_activity_not_found():
    """測試取消報名不存在的活動"""
    # Arrange - 準備測試數據
    email = "test@mergington.edu"
    invalid_activity = "Nonexistent Activity"
    
    # Act - 嘗試取消不存在活動的報名
    response = client.delete(f"/activities/{invalid_activity}/unregister?email={email}")
    
    # Assert - 驗證返回 404 錯誤
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]