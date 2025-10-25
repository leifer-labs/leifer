## Mongo

if you are using the replica version, you'll have to initialize the replica
The reason you would _want_ to use the replica version is if you want to enable watchers on collections.
This really only applies to streaming events to the web front end.

```sh
docker exec -it mongo_rs_container mongosh

rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "mongo_rs_container:27017" }]
})
# should see { "ok" : 1 }
```
