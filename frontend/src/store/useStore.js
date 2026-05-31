/**
 * EduSight AI — Global State (Zustand)
 * Manages: active student, UI state, notifications
 */

import { create } from 'zustand'

const useStore = create((set, get) => ({

  // ─── Active Student ───
  activeStudent: null,
  setActiveStudent: (student) => set({ activeStudent: student }),
  clearActiveStudent: () => set({ activeStudent: null }),

  // ─── Sidebar State ───
  sidebarCollapsed: false,
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  // ─── Notifications (toast system) ───
  notifications: [],
  addNotification: ({ type = 'info', title, message, duration = 4000 }) => {
    const id = Date.now()
    set((state) => ({
      notifications: [...state.notifications, { id, type, title, message }],
    }))
    setTimeout(() => get().removeNotification(id), duration)
  },
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  // ─── Helpers ───
  notify: {
    success: (title, message) =>
      useStore.getState().addNotification({ type: 'success', title, message }),
    error: (title, message) =>
      useStore.getState().addNotification({ type: 'error', title, message }),
    info: (title, message) =>
      useStore.getState().addNotification({ type: 'info', title, message }),
    warning: (title, message) =>
      useStore.getState().addNotification({ type: 'warning', title, message }),
  },
}))

export default useStore
