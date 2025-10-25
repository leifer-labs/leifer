// TODO// Connect to the MongoDB instance
db = db.getSiblingDB("leifer");

// === Create Collections ===
db.createCollection("users");
// === Insert Initial Admin User ===
const adminUser = {
  "username": "uberuser",
  "password": "$2b$12$n/JwZDsPwuDrO5cnXOr5/ubREo4KK/EQP1nnh0V6J/sOqBUzeqmIS",  // Replace with a bcrypt-hashed password
  "tenant_id": ObjectId(),  // Default tenant
  "role": "admin"
};
db.users.insertOne(adminUser);

//db.createCollection("tenants");
//db.createCollection("collectors");
//db.createCollection("inventory");


// === Create Indexes for Performance ===
// db.users.createIndex({ "tenant_id": 1 });
// db.inventory.createIndex({ "tenant_id": 1 });
// db.collectors.createIndex({ "tenant_id": 1 });


// === Insert Default Tenant ===
// const tenant = {
//   "_id": adminUser.tenant_id,
//   "name": "Default Tenant"
// };
// db.tenants.insertOne(tenant);

print("MongoDB initialization completed successfully.");