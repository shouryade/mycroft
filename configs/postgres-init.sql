CREATE TABLE motion_sensor_data (
    value double precision NOT NULL,
    time timestamptz DEFAULT NOW()
);

CREATE TABLE temperature_sensor_data (
    value double precision NOT NULL,
    time timestamptz DEFAULT NOW()
);

CREATE TABLE humidity_sensor_data (
    value double precision NOT NULL,
    time timestamptz DEFAULT NOW()
);

CREATE TABLE smoke_sensor_data (
    smoke double precision NOT NULL,
    co_level double precision NOT NULL,
    time timestamptz DEFAULT NOW()
);

