select sum((ru_wallclock*cost)) from %DB%.accounting where ((end_time > unix_timestamp('%START%')) and (end_time < unix_timestamp('%STOP%')) %ONLIMITS% );
