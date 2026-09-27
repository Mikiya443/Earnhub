import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import axios from "axios";
import {io} from "socket.io-client";
import "./styles.css";

const API=import.meta.env.VITE_API_URL||"http://localhost:8000/api";
const REALTIME=import.meta.env.VITE_REALTIME_URL||"http://localhost:3001";
const api=axios.create({baseURL:API});

function App(){
  const [token,setToken]=useState(localStorage.getItem("access"));
  const [user,setUser]=useState(null);
  const [tasks,setTasks]=useState([]);
  const [tx,setTx]=useState([]);
  const [page,setPage]=useState("dashboard");
  const [login,setLogin]=useState({email:"",password:""});
  const [register,setRegister]=useState({username:"",first_name:"",last_name:"",email:"",password:"",referral_code:""});
  const [message,setMessage]=useState("");

  const auth={headers:{Authorization:`Bearer ${token}`}};

  async function load(){
    if(!token)return;
    try{
      const [me,t,w]=await Promise.all([
        api.get("/auth/me/",auth),api.get("/tasks/",auth),api.get("/wallet/transactions/",auth)
      ]);
      setUser(me.data.user);setTasks(t.data);setTx(w.data);
    }catch(e){logout();}
  }
  useEffect(()=>{load()},[token]);
  useEffect(()=>{
    if(!token)return;
    const s=io(REALTIME,{auth:{token}});
    s.on("notification",p=>setMessage(p.message||"New notification"));
    return()=>s.close();
  },[token]);

  async function doLogin(e){
    e.preventDefault();
    try{const r=await api.post("/auth/login/",login);localStorage.setItem("access",r.data.access);localStorage.setItem("refresh",r.data.refresh);setToken(r.data.access);}
    catch(e){setMessage(e.response?.data?.detail||"Login failed")}
  }
  async function doRegister(e){
    e.preventDefault();
    try{const r=await api.post("/auth/register/",register);localStorage.setItem("access",r.data.tokens.access);localStorage.setItem("refresh",r.data.tokens.refresh);setToken(r.data.tokens.access);}
    catch(e){setMessage(JSON.stringify(e.response?.data||"Registration failed"))}
  }
  function logout(){localStorage.clear();setToken(null);setUser(null);}
  async function complete(id){
    try{const r=await api.post(`/tasks/${id}/complete/`,{},auth);setMessage(`You earned ₦${r.data.reward}`);load();}
    catch(e){setMessage(e.response?.data?.error||"Could not complete task")}
  }
  async function withdraw(){
    const amount=prompt("Amount to withdraw (NGN):");
    if(!amount)return;
    const account=prompt("Bank/account number:");
    if(!account)return;
    try{await api.post("/wallet/withdraw/",{amount,method:"bank",account_name:user.username,account_number:account,bank_name:""},auth);setMessage("Withdrawal request submitted");load();}
    catch(e){setMessage(JSON.stringify(e.response?.data||"Withdrawal failed"))}
  }

  if(!token)return <Auth login={login} setLogin={setLogin} register={register} setRegister={setRegister} doLogin={doLogin} doRegister={doRegister} message={message}/>;

  return <div className="app">
    <aside><div className="logo">Earn<span>hubs</span></div>
      <button className={page==="dashboard"?"active":""} onClick={()=>setPage("dashboard")}>Dashboard</button>
      <button className={page==="tasks"?"active":""} onClick={()=>setPage("tasks")}>Earn</button>
      <button className={page==="wallet"?"active":""} onClick={()=>setPage("wallet")}>Wallet</button>
      <button className={page==="referrals"?"active":""} onClick={()=>setPage("referrals")}>Referrals</button>
      <button onClick={logout}>Logout</button>
    </aside>
    <main><header><div><h1>{page[0].toUpperCase()+page.slice(1)}</h1><p>Welcome back, {user?.first_name||user?.username}</p></div><div className="avatar">{(user?.first_name||user?.username||"U")[0].toUpperCase()}</div></header>
      {message&&<div className="notice" onClick={()=>setMessage("")}>{message}</div>}
      {page==="dashboard"&&<Dashboard user={user} tasks={tasks} tx={tx}/>}
      {page==="tasks"&&<Tasks tasks={tasks} complete={complete}/>}
      {page==="wallet"&&<Wallet user={user} tx={tx} withdraw={withdraw}/>}
      {page==="referrals"&&<Referrals token={token}/>}
    </main>
  </div>
}

function Auth({login,setLogin,register,setRegister,doLogin,doRegister,message}){
 const [mode,setMode]=useState("login");
 return <div className="auth"><div className="auth-card"><div className="logo">Earn<span>hubs</span></div><h1>{mode==="login"?"Welcome back":"Create your account"}</h1>
 {message&&<div className="notice">{message}</div>}
 {mode==="login"?<form onSubmit={doLogin}><input placeholder="Email" type="email" value={login.email} onChange={e=>setLogin({...login,email:e.target.value})}/><input placeholder="Password" type="password" value={login.password} onChange={e=>setLogin({...login,password:e.target.value})}/><button>Login</button></form>:
 <form onSubmit={doRegister}><input placeholder="Username" value={register.username} onChange={e=>setRegister({...register,username:e.target.value})}/><input placeholder="First name" value={register.first_name} onChange={e=>setRegister({...register,first_name:e.target.value})}/><input placeholder="Last name" value={register.last_name} onChange={e=>setRegister({...register,last_name:e.target.value})}/><input placeholder="Email" type="email" value={register.email} onChange={e=>setRegister({...register,email:e.target.value})}/><input placeholder="Password (8+ characters)" type="password" value={register.password} onChange={e=>setRegister({...register,password:e.target.value})}/><input placeholder="Referral code (optional)" value={register.referral_code} onChange={e=>setRegister({...register,referral_code:e.target.value})}/><button>Create account</button></form>}
 <p className="switch">{mode==="login"?"Don't have an account?":"Already have an account?"} <b onClick={()=>setMode(mode==="login"?"register":"login")}>{mode==="login"?"Register":"Login"}</b></p>
 </div></div>
}

function Dashboard({user,tasks,tx}){return <><section className="cards"><Card title="Balance" value={`₦${Number(user?.wallet_balance||0).toLocaleString()}`}/><Card title="Available tasks" value={tasks.length}/><Card title="Referrals" value="View"/></section><section className="panel"><h2>Recent transactions</h2>{tx.length?<table><thead><tr><th>Type</th><th>Amount</th><th>Status</th></tr></thead><tbody>{tx.slice(0,8).map(x=><tr key={x.id}><td>{x.description||x.type}</td><td>₦{Number(x.amount).toLocaleString()}</td><td>{x.status}</td></tr>)}</tbody></table>:<p>No transactions yet.</p>}</section></>}
function Card({title,value}){return <div className="card"><small>{title}</small><strong>{value}</strong></div>}
function Tasks({tasks,complete}){return <section className="task-grid">{tasks.map(t=><div className="task" key={t.id}><span className="pill">TASK</span><h2>{t.title}</h2><p>{t.description}</p><strong>₦{Number(t.reward).toLocaleString()}</strong><button disabled={t.completed_today>=t.daily_limit} onClick={()=>complete(t.id)}>{t.completed_today>=t.daily_limit?"Completed today":"Complete task"}</button></div>)}</section>}
function Wallet({user,tx,withdraw}){return <><div className="wallet"><small>Available balance</small><strong>₦{Number(user?.wallet_balance||0).toLocaleString()}</strong><button onClick={withdraw}>Withdraw</button></div><section className="panel"><h2>Transactions</h2>{tx.map(x=><div className="tx" key={x.id}><span>{x.description||x.type}</span><b>₦{Number(x.amount).toLocaleString()}</b><small>{x.status}</small></div>)}</section></>}
function Referrals({token}){const [data,setData]=useState(null);useEffect(()=>{api.get("/referrals/",{headers:{Authorization:`Bearer ${token}`}}).then(r=>setData(r.data))},[]);return <section className="panel"><h2>Your referral code</h2><div className="code">{data?.referral_code||"Loading..."}</div><p>Share your code to invite new users.</p><h2>Your referrals</h2>{data?.referrals?.length?data.referrals.map(r=><div className="tx" key={r.id}><span>{r.username}</span><small>{r.status}</small></div>):<p>No referrals yet.</p>}</section>}

createRoot(document.getElementById("root")).render(<App/>);
