/**
 * Root Layout — wraps all pages with navbar + toast
 */

import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import ToastContainer from '../ui/Toast'

export default function RootLayout() {
  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />
      <main className="pt-12">
        <Outlet />
      </main>
      <ToastContainer />
    </div>
  )
}
