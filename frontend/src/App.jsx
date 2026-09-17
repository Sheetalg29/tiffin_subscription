import { Navigate, Route, Routes, Link, useLocation, useNavigate } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import Subscriptions from './pages/Subscriptions';
import Bills from './pages/Bills';

function Protected({children}) {
  return localStorage.getItem('tiffinflow_token') ? children : <Navigate to="/login" replace/>;
}

function Shell({children}) {
  const nav = useNavigate();
  const location = useLocation();
  const logout = () => { localStorage.removeItem('tiffinflow_token'); localStorage.removeItem('tiffinflow_user'); nav('/'); };
  const links = [['/dashboard','Dashboard'],['/customers','Customers'],['/subscriptions','Subscriptions'],['/bills','Bills']];
  return <div className="app-shell">
    <header className="topbar"><Link className="brand" to="/dashboard"><span className="brand-mark">T</span>TiffinFlow</Link><nav>{links.map(([to,label])=><Link className={location.pathname===to?'active':''} key={to} to={to}>{label}</Link>)}</nav><button className="ghost-btn" onClick={logout}>Logout</button></header>
    <main className="main-content">{children}</main>
  </div>;
}

export default function App(){
 return <Routes>
  <Route path="/" element={<Landing/>}/><Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/>
  <Route path="/dashboard" element={<Protected><Shell><Dashboard/></Shell></Protected>}/>
  <Route path="/customers" element={<Protected><Shell><Customers/></Shell></Protected>}/>
  <Route path="/subscriptions" element={<Protected><Shell><Subscriptions/></Shell></Protected>}/>
  <Route path="/bills" element={<Protected><Shell><Bills/></Shell></Protected>}/>
  <Route path="*" element={<Navigate to="/" replace/>}/>
 </Routes>;
}
