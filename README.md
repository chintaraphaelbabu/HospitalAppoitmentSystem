# HospitalAppoitmentSystem
A wxPython desktop app for hospital appointment management with user authentication, patient &amp; doctor dashboards, appointment booking/cancellation using calendar and dynamic time slots, doctor specializations, file-based data storage, registration, logout, and unit testing support.
# Hospital Appointment Manager

A wxPython desktop app for hospital appointment management. Features user authentication, appointment booking/cancellation with calendar date picker, dynamic time slots, doctor specializations, and persistent file storage.

## Features

- **User Authentication**: Secure login system for patients and doctors
- **Patient Dashboard**: 
  - Book appointments with calendar date picker
  - Dynamic time slot selection (filters already booked slots)
  - View and cancel existing appointments
  - Choose from available doctors with specializations
  
- **Doctor Dashboard**:
  - View all scheduled appointments
  - See patient details, appointment date, time, and status
  
- **User Registration**: Create new patient or doctor accounts with specializations
- **Modern GUI**: Clean, user-friendly interface with wxPython
- **Data Persistence**: Appointment and user data stored in text files
- **Logout**: Secure logout functionality

## Technologies Used

- **wxPython**: GUI framework
- **NumPy**: Data handling
- **Pillow (PIL)**: Image processing for hospital icon
- **pytest**: Unit testing
- **Python 3.x**: Core language

## Requirements

```
wxPython
numpy
Pillow
pytest
```

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install wxPython numpy Pillow pytest
   ```

## Running the Application

Navigate to the hospital directory and run:

```bash
cd hospital
python main.py
```

The application will launch with a login screen.

## Sample Credentials for Testing

### Patients
- **Username**: Raphael | **Password**: 123
- **Username**: Veeresh | **Password**: 123
- **Username**: Satish | **Password**: 123

### Doctors
- **Username**: Dr_Swapnil | **Password**: doc789 | **Specialization**: General
- **Username**: Dr_Rajnish | **Password**: 123 | **Specialization**: Orthopedic
- **Username**: Dr_Rahul | **Password**: 123 | **Specialization**: Nuclear Physicist

## Usage

### For Patients

1. **Login**: Select "patient" role, enter username and password
2. **Book Appointment**:
   - Select a date using the calendar picker
   - Available times will appear (excluding already booked slots)
   - Choose a doctor from the dropdown
   - Click "Book Appointment"
3. **View Appointments**: Your appointments display in the list below
4. **Cancel Appointment**: Select an appointment and click "Cancel Selected Appointment"
5. **Logout**: Click "Logout" to return to login screen

### For Doctors

1. **Login**: Select "doctor" role, enter credentials
2. **View Schedule**: See all appointments scheduled with you
3. **Logout**: Click "Logout" to return to login screen

### Register New User

1. Click "Register" button on login screen
2. Select role (patient or doctor)
3. Enter username and password
4. If registering as a doctor, enter specialization
5. Click "Register"

## File Structure

```
hospital/
├── main.py                 # Main application with all GUI frames and logic
├── users.txt              # User credentials and doctor specializations
├── appointments.txt       # Appointment records
├── hospital_icon.png      # Application icon (auto-generated)
├── make_icon.py           # Script to generate the hospital icon
├── __init__.py            # Package marker for pytest
└── tests/
    ├── test_appointments.py  # Unit tests for appointment functions
    └── test_users.py         # Unit tests for user management
```

## Data Format

### users.txt
```
role,username,password[,specialization]
```
Example:
```
patient,Raphael,123
doctor,Dr_Swapnil,doc789,General
```

### appointments.txt
```
patient_name,doctor_name,YYYY-MM-DD,HH:MM,status
```
Example:
```
Raphael,Dr_Swapnil,2025-12-20,14:00,booked
```

## Running Tests

To run the test suite:

```bash
pytest tests/
```

## Architecture

- **ModernPanel**: Base class for styled UI panels with consistent formatting
- **LoginFrame**: Login and registration entry point
- **PatientFrame**: Patient dashboard for booking and managing appointments
- **DoctorFrame**: Doctor dashboard for viewing appointments
- **HospitalApp**: Main wxPython application

## Key Functions

- `read_appointments()`: Reads and parses appointment data
- `write_appointments()`: Saves appointment data to file
- `load_doctors()`: Retrieves list of doctors with specializations
- `update_times_for_selected_date()`: Generates available time slots, filtering booked times

## Notes

- The application must be run from the `hospital/` directory for file paths to work correctly
- Time slots are generated in 15-minute intervals
- For today's date, available times start from the next quarter-hour after current time
- For future dates, available times start from 09:00 AM
- Appointment status can be "booked" or "completed"

## Future Enhancements

- Password hashing for security
- Doctor-side slot management UI
- Email notifications
- Appointment reminders
- Database integration (currently uses text files)
- Advanced filtering and search capabilities

## License

This project is open source and available for educational purposes.

## Author

Created as a mini project for educational purposes.
