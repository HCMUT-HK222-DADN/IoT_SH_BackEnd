# Lấy dữ liệu của tất cả sensor:
```
    message : 
        {
            "Type":"RequestUpdateSensor"
        }
        
    return : 
        {
            "Light": 24.2,
            "Temp": 38.1,
            "Humi": 41.1,
            "Motion": 0.0,
            "Type": "UpdateSensor"
        }
```

# Lấy dữ liệu hiện có của Device
```
    message :
    {
        "Type":"RequestDeviceStatus"
    }
    return:
    {
        "Type": "DeviceInit",
        "Data": [
            {
                "Device": "Quat",
                "Value": "60.000"
            },
            {
                "Device": "Den",
                "Value": "0.000"
            }
        ]
    }
```

# Lấy dữ liệu của một loại sensor cụ thể:
```    
    message : 
        {
            "Type":"RequestUpdate{type}Sensor"
        }
        + type = ["Humid","Light","Temp","Motion"]
```

# Điều khiển thiết bị
```
    message : 
        {
            "Type":"RequestDeviceControl",
            "Device": "Den", // name
            "Value": 80.0
        }
```

# Tạo session sử dụng phòng:
```
    message : 
        {
            "Type":"RequestScheduleBook",
            "Data": 
            {
                "username":"hiepngo",
                "time_start":1683093600,
                "time_end":	1683104400,
                "work_inter": "50",
                "rest_inter": "10"
            }
        }
```

# Lấy lịch sử session:
```
    message : 
        {
            "Type":"RequestSchedule",
            "UserID": 1
        }
```

# Thêm lịch (session) sử dụng phòng
```
    message :
        {
            "Type":"RequestDeviceTimerBook",
            "Device":"Quat",
            "UserID":1,
            "Value":40.0,
            "TimeStart":"2023-05-04 20:00:00"
        }
    return: 
        {

        }
```

# Lấy lịch sử hẹn giờ thiết bị:
```
    message :
        {
            "Type":"RequestDeviceTimerSchedule"
        }
    return:
        {
            "Type":"DeviceTimerSchedule",
            "Data":[
                {
                    "Device":"Quat",
                    "Value":40.0,
                    "TimeStart":"2023-05-04 13:00:00"
                },
                {
                    "Device":"Quat",
                    "Value":40.0,
                    "TimeStart":"2023-05-04 20:00:00"
                },
                {
                    "Device":"Quat",
                    "Value":40.0,
                    "TimeStart":"2023-05-04 22:00:00"
                }
            ]
        }

```

# Xóa lịch hẹn (sessions) sử dụng phòng
```

```

# Lấy lịch sử dữ liệu sensor theo SensorID
```
    message:
        {
            "Type":"RequestSensorData",
            "SensorID": 1       
        }
    return: 
        {
            "Type":"SensorData",
            "Data":
            [
                {
                    "value": "25.500",
                    "time_stamp": "2023-05-04 21:35:39"
                },
                {
                    "value": "20.700",
                    "time_stamp": "2023-05-04 21:22:44"
                }
            ]
        }
```

# Thêm lịch sử dùng thiết bị - DeviceHst
```
    message:
    {
        "Type":"RequestAddDeviceHistory",
        "UserID":1,
        "Device":"Quat",
        "Value":40.0,
        "TimeStamp":"2023-05-05 13:00:00"
    }
    return: 
    {
        "Type":"AddDeviceHistory"
    }
```

# AutoCheck and Auto Set Device
```
    message:
    {
        "Type":"RequestAutoCheckTimeStartInSetDevice"
    }
    return:
    {
        "Type":"AutoCheckTimeStartInSetDevice"
    }
```