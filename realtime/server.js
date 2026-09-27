require("dotenv").config();
const express = require("express");
const http = require("http");
const cors = require("cors");
const jwt = require("jsonwebtoken");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: process.env.FRONTEND_URL || "http://localhost:5173" }, credentials: true });

app.use(cors());
app.get("/health", (_, res) => res.json({ok:true, service:"earnhubs-realtime"}));

io.use((socket, next) => {
  try {
    const token = socket.handshake.auth?.token;
    if (!token) return next();
    socket.user = jwt.verify(token, process.env.JWT_SECRET || "change-me");
    next();
  } catch {
    next(new Error("Invalid token"));
  }
});

io.on("connection", socket => {
  if (socket.user?.sub) socket.join(`user:${socket.user.sub}`);
  socket.emit("connected", {message:"Realtime connected", time:new Date().toISOString()});
});

function notifyUser(userId, event, payload) {
  io.to(`user:${userId}`).emit(event, payload);
}

app.post("/internal/notify", express.json(), (req, res) => {
  const secret = req.headers["x-internal-secret"];
  if (!process.env.INTERNAL_SECRET || secret !== process.env.INTERNAL_SECRET) return res.status(401).json({error:"Unauthorized"});
  notifyUser(req.body.userId, req.body.event || "notification", req.body.payload || {});
  res.json({ok:true});
});

const PORT = Number(process.env.PORT || 3001);
server.listen(PORT, () => console.log(`Earnhubs realtime server on http://localhost:${PORT}`));
