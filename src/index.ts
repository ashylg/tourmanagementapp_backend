import { Hono } from 'hono'
import { cors } from 'hono/cors'

type Bindings = {
  DB: D1Database
  BUCKET: R2Bucket
}

const app = new Hono<{ Bindings: Bindings }>()

// Apply CORS to all /api/* routes
app.use('/api/*', cors())

app.get('/api/', (c) => {
  return c.json({ message: 'Hello World from Cloudflare Worker!' })
})

app.post('/api/status', async (c) => {
  try {
    const body = await c.req.json()
    const clientName = body.client_name
    
    if (!clientName) {
      return c.json({ error: 'client_name is required' }, 400)
    }

    const id = crypto.randomUUID()
    const timestamp = new Date().toISOString()
    
    await c.env.DB.prepare(
      'INSERT INTO status_checks (id, client_name, timestamp) VALUES (?, ?, ?)'
    ).bind(id, clientName, timestamp).run()
    
    return c.json({
      id,
      client_name: clientName,
      timestamp
    })
  } catch (error) {
    return c.json({ error: 'Failed to process request' }, 500)
  }
})

app.get('/api/status', async (c) => {
  try {
    const { results } = await c.env.DB.prepare(
      'SELECT * FROM status_checks ORDER BY timestamp DESC'
    ).all()
    
    return c.json(results)
  } catch (error) {
    return c.json({ error: 'Failed to fetch status checks' }, 500)
  }
})

// Export the Hono app
export default app
