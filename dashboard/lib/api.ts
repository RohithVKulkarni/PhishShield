const API_BASE_URL = "http://localhost:8000/api/v1";

export const fetcher = async (url: string) => {
    const res = await fetch(`${API_BASE_URL}${url}`);
    if (!res.ok) {
        throw new Error("An error occurred while fetching the data.");
    }
    return res.json();
};

export const api = {
    getStats: () => fetcher("/stats"),
    getEvents: () => fetcher("/events"),
    submitFeedback: (data: any) =>
        fetch(`${API_BASE_URL}/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        }).then(res => res.json()),
};
