# README

## Mongo
if you are using the replica version, you'll have to initialize the replica

```sh
docker exec -it mongodb_rs mongosh

rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "localhost:27017" }]
})
# should see { "ok" : 1 }
```
