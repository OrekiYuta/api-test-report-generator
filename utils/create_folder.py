import os
from utils.PathManager import load_path_manager as lpm

folder_input_jaeger = str(lpm.input("Jaeger-Screenshot"))
folder_input_sql_statement = str(lpm.input("SQL-Statement"))

base_directory = folder_input_sql_statement

#  api  count: 2
cv_item = ['API-001', 'API-002']
# batch api count: 25
batch_item = ['BAT-001', 'BAT-002', 'BAT-003', 'BAT-017', 'BAT-024',
              'BAT-025', 'BAT-004', 'BAT-005', 'BAT-008', 'BAT-007',
              'BAT-009', 'BAT-018', 'BAT-010', 'BAT-019', 'BAT-006',
              'BAT-012', 'BAT-021', 'BAT-013', 'BAT-022', 'BAT-011',
              'BAT-020', 'BAT-014', 'BAT-015', 'BAT-023', 'BAT-016']

#  admin api count: 11
admin_item = ['API-077', 'API-078', 'API-079', 'API-080',
              'API-081', 'API-082', 'API-086', 'API-087',
              'API-083', 'API-084', 'API-085']

# common api  count: 62
common_item = ['API-007', 'API-021', 'API-022', 'API-071', 'API-023', 'API-024',
               'API-026', 'API-072', 'API-027', 'API-028', 'API-029', 'API-063',
               'API-019', 'API-020', 'API-069', 'API-006', 'API-068', 'API-008',
               'API-009', 'API-016', 'API-017', 'API-018', 'API-044', 'API-045',
               'API-074', 'API-046', 'API-047', 'API-048', 'API-041', 'API-042',
               'API-043', 'API-049', 'API-050', 'API-051', 'API-075', 'API-058',
               'API-059', 'API-060', 'API-076', 'API-038', 'API-039', 'API-040',
               'API-052', 'API-053', 'API-054', 'API-055', 'API-056', 'API-057',
               'API-061', 'API-062', 'API-010', 'API-011', 'API-013', 'API-014',
               'API-031', 'API-032', 'API-033', 'API-034', 'API-035', 'API-036',
               'API-003', 'API-004']

create_item = admin_item
for item in create_item:
    directory_path = os.path.join(base_directory, item)
    os.makedirs(directory_path, exist_ok=True)
