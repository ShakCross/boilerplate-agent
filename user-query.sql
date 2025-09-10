SELECT
    u.id,
    u."firstName",
    u."lastName",
    u."companyName",
    u.bio,
    u."companyOverview",
    u."serviceOfferings",
    u."professionalLicenses",
    u.certifications,
    u.address,
    u.state,
    u.city,
    u."zipCode",
    u.latitude,
    u.longitude,
    u.geolocation,
    COALESCE(string_agg(DISTINCT c.name, ', '), '')  AS categories,
    COALESCE(string_agg(DISTINCT s.name, ', '), '')  AS specialties,
    COALESCE(string_agg(DISTINCT e.name, ', '), '')  AS expertises,
    COALESCE(string_agg(DISTINCT sr.name, ', '), '') AS service_ranges
FROM "user" u
LEFT JOIN user_category      uc  ON uc."userId"        = u.id
LEFT JOIN category           c   ON c.id               = uc."categoryId"
LEFT JOIN user_specialty     us  ON us."userId"        = u.id
LEFT JOIN specialty          s   ON s.id               = us."specialtyId"
LEFT JOIN user_expertise     ue  ON ue."userId"        = u.id
LEFT JOIN expertise          e   ON e.id               = ue."expertiseId"
LEFT JOIN user_service_range usr ON usr."userId"       = u.id
LEFT JOIN service_range      sr  ON sr.id              = usr."serviceRangeId"
WHERE u."roleId" = 2
GROUP BY
    u.id, u."firstName", u."lastName", u."companyName",
    u.bio, u."companyOverview", u."serviceOfferings",
    u."professionalLicenses", u.certifications,
    u.address, u.state, u.city, u."zipCode",
    u.latitude, u.longitude, u.geolocation;
