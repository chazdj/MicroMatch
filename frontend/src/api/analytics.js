import api from "./api";

export const getStudentAnalytics = () =>
  api.get("/analytics/student").then((res) => res.data);

export const getOrganizationAnalytics = () =>
  api.get("/analytics/organization").then((res) => res.data);