# Streamlit Cloud Deployment Guide

This guide provides step-by-step instructions to deploy your Production Analytics Dashboard on Streamlit Cloud, making it accessible 24/7 via a public URL. The process involves uploading the application code to a GitHub repository and then connecting that repository to Streamlit Cloud.

## Prerequisites

Before you begin, you will need a **GitHub account**. If you don’t have one, you can create a free account at [https://github.com/join](https://github.com/join).

## Deployment Steps

The deployment process is broken down into three main parts:

1.  **Create a GitHub Repository**
2.  **Upload Application Files**
3.  **Deploy on Streamlit Cloud**

---

### Step 1: Create a GitHub Repository

A GitHub repository will store your application’s code, which Streamlit Cloud will use for deployment.

1.  **Log in to GitHub** and go to your dashboard.
2.  Click the **"New"** button next to your repositories list, or navigate to [https://github.com/new](https://github.com/new).
3.  **Repository Name**: Give your repository a name, for example, `production-analytics-dashboard`.
4.  **Description**: Optionally, add a brief description like "Streamlit dashboard for production analytics."
5.  **Visibility**: Select **"Public"**. Streamlit Cloud’s free tier requires the repository to be public.
6.  **Initialize**: Do **not** initialize the repository with a README, .gitignore, or license at this stage, as we have already created these files.
7.  Click **"Create repository"**.

![Create GitHub Repo](https://i.imgur.com/gJ9wL4g.png)

---

### Step 2: Upload Application Files

Next, you need to upload the application files I have prepared for you into your new GitHub repository.

1.  On your new repository's main page, click the **"uploading an existing file"** link.

    ![Upload Files](https://i.imgur.com/9vGv1j2.png)

2.  **Unzip the `production_analytics_deploy.zip`** file that I will provide. You should see the following files:
    - `app.py`
    - `requirements.txt`
    - `.gitignore`
    - `README.md`
    - `DEPLOYMENT_GUIDE.md` (this file)

3.  **Drag and drop** all of these files (except the zip file itself) into the GitHub upload area.

4.  **Commit Changes**: Once the files are uploaded, scroll down to the "Commit changes" section.
    -   You can leave the default commit message ("Add files via upload").
    -   Ensure the **"Commit directly to the `main` branch"** option is selected.
    -   Click the **"Commit changes"** button.

    ![Commit Files](https://i.imgur.com/uQy3g6Y.png)

Your repository now contains all the necessary code for the application.

---

### Step 3: Deploy on Streamlit Cloud

Now you can connect your GitHub repository to Streamlit Cloud to deploy the app.

1.  **Sign Up/Log In**: Go to [https://share.streamlit.io](https://share.streamlit.io) and sign up for a free account using your GitHub account. Authorize Streamlit to access your GitHub repositories when prompted.

2.  **Create a New App**: From your Streamlit Cloud dashboard, click the **"New app"** button.

3.  **Configure Deployment**: Fill in the deployment settings:
    -   **Repository**: Select the GitHub repository you just created (e.g., `your-username/production-analytics-dashboard`).
    -   **Branch**: Ensure it is set to `main`.
    -   **Main file path**: This should automatically be set to `app.py`. If not, enter `app.py`.
    -   **App URL**: You can customize the URL for your app if you wish.

    ![Streamlit Deploy Config](https://i.imgur.com/nZ4h0fT.png)

4.  **Deploy**: Click the **"Deploy!"** button.

Streamlit will now build and deploy your application. You can watch the progress in the logs. The first deployment may take a few minutes as it installs all the required packages.

Once it's finished, your application will be live at the URL you specified! You and your team can now access it from any browser, upload the production report, and view the analytics 24/7.

---

## Maintaining Your Application

-   **Updates**: If you need any changes to the app in the future, I can provide you with updated files. You would then upload the new files to your GitHub repository, and Streamlit Cloud will automatically detect the changes and redeploy your app.
-   **Secrets**: This application does not require any secret keys. If you add features that need API keys in the future, you can manage them securely using Streamlit Cloud's secrets management.
