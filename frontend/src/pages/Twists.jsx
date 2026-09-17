import {useEffect, useState} from 'react';
import api from '../services/api';

export default function Twists() {
  const [clockDate, setClockDate] = useState(new Date().toISOString().slice(0,10));
  const [clockResult, setClockResult] = useState(null);
  const [file, setFile] = useState(null);
  const [importResult, setImportResult] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [subs, setSubs] = useState([]);
  const [transfer, setTransfer] = useState({subscription_id:'', new_customer_id:'', transfer_date:''});
  const [transferResult, setTransferResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      api.get('/customers', {params:{limit:100}}),
      api.get('/subscriptions')
    ]).then(([c,s]) => {
      setCustomers(c.data.items);
      setSubs(s.data.items);
    }).catch(e => setError(e.response?.data?.detail || 'Could not load data'));
  }, []);

  const runClock = async () => {
    try {
      setError('');
      const r = await api.post('/clock', null, {params:{today:clockDate}});
      setClockResult(r.data);
    } catch(e) { setError(e.response?.data?.detail || 'Clock failed'); }
  };

  const importCsv = async () => {
    if (!file) return;
    try {
      setError('');
      const form = new FormData();
      form.append('file', file);
      const r = await api.post('/import/customers', form);
      setImportResult(r.data);
    } catch(e) { setError(e.response?.data?.detail || 'Import failed'); }
  };

  const doTransfer = async () => {
    try {
      setError('');
      const r = await api.post(`/subscriptions/${transfer.subscription_id}/transfer`, {
        new_customer_id: Number(transfer.new_customer_id),
        transfer_date: transfer.transfer_date
      });
      setTransferResult(r.data);
    } catch(e) { setError(e.response?.data?.detail || 'Transfer failed'); }
  };

  return <div>
    <div className="page-head">
      <div>
        <div className="section-label">ADVANCED FEATURES</div>
        <h1>Twist controls</h1>
        <p className="muted">Daily delivery notifications, mid-cycle transfers, and messy CSV imports.</p>
      </div>
    </div>

    {error && <div className="alert error">{error}</div>}

    <div className="billing-layout">
      <div className="panel calculator">
        <h2>1. Daily delivery clock</h2>
        <p className="muted">Creates idempotent DELIVERY_DUE events in the notification outbox.</p>
        <div className="form-stack">
          <label>Run date<input type="date" value={clockDate} onChange={e=>setClockDate(e.target.value)}/></label>
          <button className="btn btn-primary full" onClick={runClock}>Run clock</button>
        </div>
        {clockResult && <div className="bill-result">
          <b>{clockResult.message}</b>
          <p>{clockResult.date} • {clockResult.due_notifications_created} notification(s) created</p>
        </div>}
      </div>

      <div className="panel calculator">
        <h2>2. Mid-cycle transfer</h2>
        <p className="muted">The plan and cycle continue; billing allocations are split by served days.</p>
        <div className="form-stack">
          <label>Subscription<select value={transfer.subscription_id} onChange={e=>setTransfer({...transfer,subscription_id:e.target.value})}>
            <option value="">Select subscription</option>
            {subs.map(s=><option key={s.id} value={s.id}>#{s.id} • {s.customer_name} • {s.plan_name}</option>)}
          </select></label>
          <label>New customer<select value={transfer.new_customer_id} onChange={e=>setTransfer({...transfer,new_customer_id:e.target.value})}>
            <option value="">Select customer</option>
            {customers.map(c=><option key={c.id} value={c.id}>{c.name} • {c.phone}</option>)}
          </select></label>
          <label>Transfer date<input type="date" value={transfer.transfer_date} onChange={e=>setTransfer({...transfer,transfer_date:e.target.value})}/></label>
          <button className="btn btn-primary full" disabled={!transfer.subscription_id || !transfer.new_customer_id || !transfer.transfer_date} onClick={doTransfer}>Transfer subscription</button>
        </div>
        {transferResult && <div className="bill-result"><b>Transfer recorded</b><p>#{transferResult.subscription_id}: customer {transferResult.from_customer_id} → {transferResult.to_customer_id} from {transferResult.transfer_date}</p></div>}
      </div>
    </div>

    <div className="panel calculator" style={{marginTop:'20px'}}>
      <h2>3. Messy customer CSV import</h2>
      <p className="muted">Normalizes phones/dates, skips duplicate phones, and reports rejected rows.</p>
      <div className="form-stack">
        <input type="file" accept=".csv" onChange={e=>setFile(e.target.files?.[0] || null)}/>
        <button className="btn btn-primary" disabled={!file} onClick={importCsv}>Import customers</button>
      </div>
      {importResult && <div className="bill-result">
        <div className="bill-metrics">
          <Metric label="Total" value={importResult.total}/>
          <Metric label="Imported" value={importResult.imported}/>
          <Metric label="Duplicates" value={importResult.duplicates}/>
          <Metric label="Rejected" value={importResult.rejected}/>
        </div>
        {importResult.rejected_rows?.length > 0 &&
          <div className="panel" style={{marginTop:'14px'}}>
            <b>Rejected rows</b>
            {importResult.rejected_rows.map(x=><p key={x.row}>Row {x.row}: {x.reason}</p>)}
          </div>}
      </div>}
    </div>
  </div>
}

function Metric({label,value}) {
  return <div><small>{label}</small><strong>{value}</strong></div>
}
