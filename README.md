# SoftwareBERTSaludCMV

[![Demo](https://img.youtube.com/vi/RrqTUxrPb2g/hqdefault.jpg)](https://www.youtube.com/embed/RrqTUxrPb2g)

SoftwareBERTSaludCMV is an advanced data classification tool designed for the Municipal Corporation of Valparaíso to assist in the evaluation and analysis of healthcare-related feedback. Utilizing a sophisticated BERT (Bidirectional Encoder Representations from Transformers) model, this software adeptly categorizes large volumes of anonymous user data into a MongoDB database. The classified outcomes are marked as '0', '1', or '2', indicating 'irrelevant', 'negative', or 'positive', respectively, providing a clear and actionable insight into patient sentiments and experiences.

**Key Features:**

- **Data Management Interface:** A user-friendly GUI allows healthcare administrators to seamlessly explore, search, and filter through patient data entries. Users can query data by various attributes including age, gender, health center, frequency of visits, satisfaction levels, recommendations, open comments, date of feedback, and classification label.
- **Advanced Search Capabilities:** The search function is equipped to handle complex queries such as date ranges, partial text matches, and category-specific searches, ensuring that users can locate precise information swiftly.
- **BERT Model Integration:** Leveraging the BERT model's natural language processing capabilities, the software accurately classifies open-ended patient comments into predefined categories that reflect the sentiment and relevance of the feedback.
- **Database Connectivity:** Direct integration with MongoDB allows for robust data storage and retrieval, providing a secure and efficient backend for the application.
- **Data Export Function:** Users have the option to export the filtered and processed data into an Excel spreadsheet for further analysis or reporting purposes.

**How it Works:**

1. **Initialization:** On launching the application, users are greeted with a main window that displays the current statistics of total and uncategorized documents.
2. **Data Exploration:** The 'Explore Data' option launches a new window providing tools to search and view data entries in a table format with sortable columns.
3. **Data Classification:** A 'Classify Data' button triggers the BERT model to process uncategorized entries and assign them the appropriate sentiment label.
4. **Export Options:** After filtering and reviewing data, users can export the dataset to Excel with the click of a button for offline analysis or presentations.

**Benefits:**

- Provides a quick and efficient method for sorting patient feedback, allowing healthcare providers to prioritize responses and identify areas for improvement.
- Offers a dark-themed, visually comfortable interface that reduces eye strain during extended use.
- Facilitates data-driven decision-making with an automated process that reduces manual classification efforts.
- Enhances patient care by systematically identifying and addressing common concerns or praises brought up in user feedback.

SoftwareBERTSaludCMV empowers healthcare administrators with a potent tool to harness the power of machine learning for the betterment of service quality and patient satisfaction in Valparaíso's health centers.
