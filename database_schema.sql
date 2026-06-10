--
-- PostgreSQL database dump
--

\restrict O7aCB2rHYr7gC7AqsJ39K2pYLIPcOXt92Qo0MtgljQhGokUWyZw87v7laiFBQ8u

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-04-26 05:33:10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5 (class 2615 OID 65536)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 5201 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 246 (class 1259 OID 98333)
-- Name: ai_detection_records; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_detection_records (
    record_id integer NOT NULL,
    user_id integer NOT NULL,
    original_text text NOT NULL,
    ai_score double precision NOT NULL,
    result_detail jsonb,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.ai_detection_records OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 98332)
-- Name: ai_detection_records_record_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ai_detection_records_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ai_detection_records_record_id_seq OWNER TO postgres;

--
-- TOC entry 5203 (class 0 OID 0)
-- Dependencies: 245
-- Name: ai_detection_records_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ai_detection_records_record_id_seq OWNED BY public.ai_detection_records.record_id;


--
-- TOC entry 234 (class 1259 OID 65667)
-- Name: ai_read_analytics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ai_read_analytics (
    analytic_id integer NOT NULL,
    material_id integer NOT NULL,
    user_id integer NOT NULL,
    reading_duration integer,
    ai_score numeric(5,2),
    recommendation text,
    analyzed_at timestamp without time zone DEFAULT now(),
    knowledge_points json,
    methodology_feat text,
    mermaid_code text,
    content_summary text,
    memo text
);


ALTER TABLE public.ai_read_analytics OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 65666)
-- Name: ai_read_analytics_analytic_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ai_read_analytics_analytic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ai_read_analytics_analytic_id_seq OWNER TO postgres;

--
-- TOC entry 5204 (class 0 OID 0)
-- Dependencies: 233
-- Name: ai_read_analytics_analytic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ai_read_analytics_analytic_id_seq OWNED BY public.ai_read_analytics.analytic_id;


--
-- TOC entry 220 (class 1259 OID 65538)
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 65537)
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_category_id_seq OWNER TO postgres;

--
-- TOC entry 5205 (class 0 OID 0)
-- Dependencies: 219
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- TOC entry 252 (class 1259 OID 114745)
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_messages (
    id integer NOT NULL,
    session_id integer,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.chat_messages OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 114744)
-- Name: chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_messages_id_seq OWNER TO postgres;

--
-- TOC entry 5206 (class 0 OID 0)
-- Dependencies: 251
-- Name: chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;


--
-- TOC entry 250 (class 1259 OID 114730)
-- Name: chat_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_sessions (
    id integer NOT NULL,
    title character varying(255) DEFAULT '新对话'::character varying,
    active_file_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.chat_sessions OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 114729)
-- Name: chat_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_sessions_id_seq OWNER TO postgres;

--
-- TOC entry 5207 (class 0 OID 0)
-- Dependencies: 249
-- Name: chat_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_sessions_id_seq OWNED BY public.chat_sessions.id;


--
-- TOC entry 238 (class 1259 OID 65707)
-- Name: conversations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conversations (
    conversation_id integer NOT NULL,
    user_id integer NOT NULL,
    material_id integer,
    message text NOT NULL,
    role character varying(20),
    created_at timestamp without time zone DEFAULT now(),
    session_id character varying(36) NOT NULL,
    context_summary text
);


ALTER TABLE public.conversations OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 65706)
-- Name: conversations_conversation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.conversations_conversation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.conversations_conversation_id_seq OWNER TO postgres;

--
-- TOC entry 5208 (class 0 OID 0)
-- Dependencies: 237
-- Name: conversations_conversation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.conversations_conversation_id_seq OWNED BY public.conversations.conversation_id;


--
-- TOC entry 248 (class 1259 OID 114717)
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    id integer NOT NULL,
    filename character varying(255) NOT NULL,
    file_type character varying(50) NOT NULL,
    content_path text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.documents OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 114716)
-- Name: documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.documents_id_seq OWNER TO postgres;

--
-- TOC entry 5209 (class 0 OID 0)
-- Dependencies: 247
-- Name: documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.documents_id_seq OWNED BY public.documents.id;


--
-- TOC entry 242 (class 1259 OID 65755)
-- Name: fines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fines (
    fine_id integer NOT NULL,
    loan_id integer NOT NULL,
    user_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    status character varying(20),
    issued_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.fines OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 65754)
-- Name: fines_fine_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fines_fine_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fines_fine_id_seq OWNER TO postgres;

--
-- TOC entry 5210 (class 0 OID 0)
-- Dependencies: 241
-- Name: fines_fine_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fines_fine_id_seq OWNED BY public.fines.fine_id;


--
-- TOC entry 240 (class 1259 OID 65732)
-- Name: loans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.loans (
    loan_id integer NOT NULL,
    item_id integer NOT NULL,
    user_id integer NOT NULL,
    loan_date timestamp without time zone DEFAULT now(),
    due_date date NOT NULL,
    return_date date,
    status character varying(20),
    reading_priority integer
);


ALTER TABLE public.loans OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 65731)
-- Name: loans_loan_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.loans_loan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.loans_loan_id_seq OWNER TO postgres;

--
-- TOC entry 5211 (class 0 OID 0)
-- Dependencies: 239
-- Name: loans_loan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.loans_loan_id_seq OWNED BY public.loans.loan_id;


--
-- TOC entry 224 (class 1259 OID 65568)
-- Name: materials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.materials (
    material_id integer NOT NULL,
    title character varying(200) NOT NULL,
    author character varying(500),
    material_type character varying(50),
    isbn_doi character varying(50),
    publish_year integer,
    category_id integer,
    abstract_summary text,
    doi_link character varying(255),
    file_path character varying(500),
    is_local boolean,
    vector_index character varying(100),
    project_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.materials OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 65625)
-- Name: materials_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.materials_items (
    item_id integer NOT NULL,
    material_id integer NOT NULL,
    barcode character varying(50) NOT NULL,
    status character varying(20),
    location_shelf character varying(50),
    acquired_date date,
    content_chunk text
);


ALTER TABLE public.materials_items OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 65624)
-- Name: materials_items_item_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.materials_items_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.materials_items_item_id_seq OWNER TO postgres;

--
-- TOC entry 5212 (class 0 OID 0)
-- Dependencies: 229
-- Name: materials_items_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.materials_items_item_id_seq OWNED BY public.materials_items.item_id;


--
-- TOC entry 223 (class 1259 OID 65567)
-- Name: materials_material_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.materials_material_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.materials_material_id_seq OWNER TO postgres;

--
-- TOC entry 5213 (class 0 OID 0)
-- Dependencies: 223
-- Name: materials_material_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.materials_material_id_seq OWNED BY public.materials.material_id;


--
-- TOC entry 228 (class 1259 OID 65603)
-- Name: mentor_student; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mentor_student (
    id integer NOT NULL,
    mentor_id integer NOT NULL,
    student_id integer NOT NULL,
    assigned_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.mentor_student OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 65602)
-- Name: mentor_student_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mentor_student_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mentor_student_id_seq OWNER TO postgres;

--
-- TOC entry 5214 (class 0 OID 0)
-- Dependencies: 227
-- Name: mentor_student_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mentor_student_id_seq OWNED BY public.mentor_student.id;


--
-- TOC entry 244 (class 1259 OID 90113)
-- Name: research_projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.research_projects (
    project_id integer NOT NULL,
    user_id integer NOT NULL,
    major character varying(100) NOT NULL,
    topic character varying(255) NOT NULL,
    outline jsonb,
    recommended_refs jsonb,
    status character varying(50) DEFAULT 'drafting'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    research_plan json
);


ALTER TABLE public.research_projects OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 90112)
-- Name: research_projects_project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.research_projects_project_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.research_projects_project_id_seq OWNER TO postgres;

--
-- TOC entry 5215 (class 0 OID 0)
-- Dependencies: 243
-- Name: research_projects_project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.research_projects_project_id_seq OWNED BY public.research_projects.project_id;


--
-- TOC entry 232 (class 1259 OID 65645)
-- Name: reservations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservations (
    reservation_id integer NOT NULL,
    user_id integer NOT NULL,
    material_id integer NOT NULL,
    reserved_date timestamp without time zone DEFAULT now(),
    expiry_date date,
    status character varying(20)
);


ALTER TABLE public.reservations OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 65644)
-- Name: reservations_reservation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservations_reservation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservations_reservation_id_seq OWNER TO postgres;

--
-- TOC entry 5216 (class 0 OID 0)
-- Dependencies: 231
-- Name: reservations_reservation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservations_reservation_id_seq OWNED BY public.reservations.reservation_id;


--
-- TOC entry 236 (class 1259 OID 65691)
-- Name: semantic_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.semantic_tags (
    tag_id integer NOT NULL,
    material_id integer NOT NULL,
    tag_name character varying(100) NOT NULL,
    tag_type character varying(50),
    confidence numeric(4,3)
);


ALTER TABLE public.semantic_tags OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 65690)
-- Name: semantic_tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.semantic_tags_tag_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.semantic_tags_tag_id_seq OWNER TO postgres;

--
-- TOC entry 5217 (class 0 OID 0)
-- Dependencies: 235
-- Name: semantic_tags_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.semantic_tags_tag_id_seq OWNED BY public.semantic_tags.tag_id;


--
-- TOC entry 226 (class 1259 OID 65587)
-- Name: user_interests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_interests (
    interest_id integer NOT NULL,
    user_id integer NOT NULL,
    category_name character varying(100),
    weight numeric(3,2),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.user_interests OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 65586)
-- Name: user_interests_interest_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_interests_interest_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_interests_interest_id_seq OWNER TO postgres;

--
-- TOC entry 5218 (class 0 OID 0)
-- Dependencies: 225
-- Name: user_interests_interest_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_interests_interest_id_seq OWNED BY public.user_interests.interest_id;


--
-- TOC entry 222 (class 1259 OID 65550)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    role character varying(20) NOT NULL,
    password_hash character varying(255) NOT NULL,
    date_of_birth date,
    contact_details character varying(255),
    created_at timestamp without time zone DEFAULT now(),
    status character varying(20),
    credit_score integer
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 65549)
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- TOC entry 5219 (class 0 OID 0)
-- Dependencies: 221
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- TOC entry 4961 (class 2604 OID 98336)
-- Name: ai_detection_records record_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_detection_records ALTER COLUMN record_id SET DEFAULT nextval('public.ai_detection_records_record_id_seq'::regclass);


--
-- TOC entry 4948 (class 2604 OID 65670)
-- Name: ai_read_analytics analytic_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_read_analytics ALTER COLUMN analytic_id SET DEFAULT nextval('public.ai_read_analytics_analytic_id_seq'::regclass);


--
-- TOC entry 4936 (class 2604 OID 65541)
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- TOC entry 4968 (class 2604 OID 114748)
-- Name: chat_messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- TOC entry 4965 (class 2604 OID 114733)
-- Name: chat_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.chat_sessions_id_seq'::regclass);


--
-- TOC entry 4951 (class 2604 OID 65710)
-- Name: conversations conversation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversations ALTER COLUMN conversation_id SET DEFAULT nextval('public.conversations_conversation_id_seq'::regclass);


--
-- TOC entry 4963 (class 2604 OID 114720)
-- Name: documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents ALTER COLUMN id SET DEFAULT nextval('public.documents_id_seq'::regclass);


--
-- TOC entry 4955 (class 2604 OID 65758)
-- Name: fines fine_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fines ALTER COLUMN fine_id SET DEFAULT nextval('public.fines_fine_id_seq'::regclass);


--
-- TOC entry 4953 (class 2604 OID 65735)
-- Name: loans loan_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans ALTER COLUMN loan_id SET DEFAULT nextval('public.loans_loan_id_seq'::regclass);


--
-- TOC entry 4939 (class 2604 OID 65571)
-- Name: materials material_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials ALTER COLUMN material_id SET DEFAULT nextval('public.materials_material_id_seq'::regclass);


--
-- TOC entry 4945 (class 2604 OID 65628)
-- Name: materials_items item_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials_items ALTER COLUMN item_id SET DEFAULT nextval('public.materials_items_item_id_seq'::regclass);


--
-- TOC entry 4943 (class 2604 OID 65606)
-- Name: mentor_student id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mentor_student ALTER COLUMN id SET DEFAULT nextval('public.mentor_student_id_seq'::regclass);


--
-- TOC entry 4957 (class 2604 OID 90116)
-- Name: research_projects project_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.research_projects ALTER COLUMN project_id SET DEFAULT nextval('public.research_projects_project_id_seq'::regclass);


--
-- TOC entry 4946 (class 2604 OID 65648)
-- Name: reservations reservation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations ALTER COLUMN reservation_id SET DEFAULT nextval('public.reservations_reservation_id_seq'::regclass);


--
-- TOC entry 4950 (class 2604 OID 65694)
-- Name: semantic_tags tag_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.semantic_tags ALTER COLUMN tag_id SET DEFAULT nextval('public.semantic_tags_tag_id_seq'::regclass);


--
-- TOC entry 4941 (class 2604 OID 65590)
-- Name: user_interests interest_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_interests ALTER COLUMN interest_id SET DEFAULT nextval('public.user_interests_interest_id_seq'::regclass);


--
-- TOC entry 4937 (class 2604 OID 65553)
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- TOC entry 5018 (class 2606 OID 98345)
-- Name: ai_detection_records ai_detection_records_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_detection_records
    ADD CONSTRAINT ai_detection_records_pkey PRIMARY KEY (record_id);


--
-- TOC entry 4999 (class 2606 OID 65678)
-- Name: ai_read_analytics ai_read_analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_read_analytics
    ADD CONSTRAINT ai_read_analytics_pkey PRIMARY KEY (analytic_id);


--
-- TOC entry 4971 (class 2606 OID 65547)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- TOC entry 5026 (class 2606 OID 114756)
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- TOC entry 5024 (class 2606 OID 114738)
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);


--
-- TOC entry 5005 (class 2606 OID 65719)
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (conversation_id);


--
-- TOC entry 5022 (class 2606 OID 114728)
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- TOC entry 5011 (class 2606 OID 65765)
-- Name: fines fines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fines
    ADD CONSTRAINT fines_pkey PRIMARY KEY (fine_id);


--
-- TOC entry 5009 (class 2606 OID 65742)
-- Name: loans loans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_pkey PRIMARY KEY (loan_id);


--
-- TOC entry 4981 (class 2606 OID 65579)
-- Name: materials materials_isbn_doi_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_isbn_doi_key UNIQUE (isbn_doi);


--
-- TOC entry 4992 (class 2606 OID 65637)
-- Name: materials_items materials_items_barcode_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials_items
    ADD CONSTRAINT materials_items_barcode_key UNIQUE (barcode);


--
-- TOC entry 4994 (class 2606 OID 65635)
-- Name: materials_items materials_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials_items
    ADD CONSTRAINT materials_items_pkey PRIMARY KEY (item_id);


--
-- TOC entry 4983 (class 2606 OID 65577)
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (material_id);


--
-- TOC entry 4989 (class 2606 OID 65612)
-- Name: mentor_student mentor_student_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mentor_student
    ADD CONSTRAINT mentor_student_pkey PRIMARY KEY (id);


--
-- TOC entry 5016 (class 2606 OID 90127)
-- Name: research_projects research_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.research_projects
    ADD CONSTRAINT research_projects_pkey PRIMARY KEY (project_id);


--
-- TOC entry 4997 (class 2606 OID 65654)
-- Name: reservations reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_pkey PRIMARY KEY (reservation_id);


--
-- TOC entry 5003 (class 2606 OID 65699)
-- Name: semantic_tags semantic_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.semantic_tags
    ADD CONSTRAINT semantic_tags_pkey PRIMARY KEY (tag_id);


--
-- TOC entry 4986 (class 2606 OID 65595)
-- Name: user_interests user_interests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_interests
    ADD CONSTRAINT user_interests_pkey PRIMARY KEY (interest_id);


--
-- TOC entry 4975 (class 2606 OID 65565)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4977 (class 2606 OID 65563)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- TOC entry 5019 (class 1259 OID 98352)
-- Name: idx_ai_detection_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ai_detection_created_at ON public.ai_detection_records USING btree (created_at DESC);


--
-- TOC entry 5020 (class 1259 OID 98351)
-- Name: idx_ai_detection_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ai_detection_user_id ON public.ai_detection_records USING btree (user_id);


--
-- TOC entry 5013 (class 1259 OID 90134)
-- Name: idx_project_major; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_project_major ON public.research_projects USING btree (major);


--
-- TOC entry 5014 (class 1259 OID 90133)
-- Name: idx_project_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_project_user ON public.research_projects USING btree (user_id);


--
-- TOC entry 5000 (class 1259 OID 65689)
-- Name: ix_ai_read_analytics_analytic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ai_read_analytics_analytic_id ON public.ai_read_analytics USING btree (analytic_id);


--
-- TOC entry 4972 (class 1259 OID 65548)
-- Name: ix_categories_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_categories_category_id ON public.categories USING btree (category_id);


--
-- TOC entry 5006 (class 1259 OID 65730)
-- Name: ix_conversations_conversation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_conversations_conversation_id ON public.conversations USING btree (conversation_id);


--
-- TOC entry 5012 (class 1259 OID 65776)
-- Name: ix_fines_fine_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fines_fine_id ON public.fines USING btree (fine_id);


--
-- TOC entry 5007 (class 1259 OID 65753)
-- Name: ix_loans_loan_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_loans_loan_id ON public.loans USING btree (loan_id);


--
-- TOC entry 4990 (class 1259 OID 65643)
-- Name: ix_materials_items_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_materials_items_item_id ON public.materials_items USING btree (item_id);


--
-- TOC entry 4978 (class 1259 OID 65585)
-- Name: ix_materials_material_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_materials_material_id ON public.materials USING btree (material_id);


--
-- TOC entry 4979 (class 1259 OID 90150)
-- Name: ix_materials_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_materials_project_id ON public.materials USING btree (project_id);


--
-- TOC entry 4987 (class 1259 OID 65623)
-- Name: ix_mentor_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mentor_student_id ON public.mentor_student USING btree (id);


--
-- TOC entry 4995 (class 1259 OID 65665)
-- Name: ix_reservations_reservation_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reservations_reservation_id ON public.reservations USING btree (reservation_id);


--
-- TOC entry 5001 (class 1259 OID 65705)
-- Name: ix_semantic_tags_tag_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_semantic_tags_tag_id ON public.semantic_tags USING btree (tag_id);


--
-- TOC entry 4984 (class 1259 OID 65601)
-- Name: ix_user_interests_interest_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_interests_interest_id ON public.user_interests USING btree (interest_id);


--
-- TOC entry 4973 (class 1259 OID 65566)
-- Name: ix_users_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_user_id ON public.users USING btree (user_id);


--
-- TOC entry 5046 (class 2606 OID 98346)
-- Name: ai_detection_records ai_detection_records_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_detection_records
    ADD CONSTRAINT ai_detection_records_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 5036 (class 2606 OID 65679)
-- Name: ai_read_analytics ai_read_analytics_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_read_analytics
    ADD CONSTRAINT ai_read_analytics_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(material_id);


--
-- TOC entry 5037 (class 2606 OID 65684)
-- Name: ai_read_analytics ai_read_analytics_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ai_read_analytics
    ADD CONSTRAINT ai_read_analytics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5048 (class 2606 OID 114757)
-- Name: chat_messages chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id) ON DELETE CASCADE;


--
-- TOC entry 5047 (class 2606 OID 114766)
-- Name: chat_sessions chat_sessions_active_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_active_file_id_fkey FOREIGN KEY (active_file_id) REFERENCES public.materials(material_id) ON DELETE SET NULL;


--
-- TOC entry 5039 (class 2606 OID 65725)
-- Name: conversations conversations_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(material_id);


--
-- TOC entry 5040 (class 2606 OID 65720)
-- Name: conversations conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5043 (class 2606 OID 65766)
-- Name: fines fines_loan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fines
    ADD CONSTRAINT fines_loan_id_fkey FOREIGN KEY (loan_id) REFERENCES public.loans(loan_id);


--
-- TOC entry 5044 (class 2606 OID 65771)
-- Name: fines fines_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fines
    ADD CONSTRAINT fines_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5027 (class 2606 OID 90151)
-- Name: materials fk_materials_project_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT fk_materials_project_id FOREIGN KEY (project_id) REFERENCES public.research_projects(project_id) ON DELETE SET NULL;


--
-- TOC entry 5028 (class 2606 OID 90135)
-- Name: materials fk_project; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT fk_project FOREIGN KEY (project_id) REFERENCES public.research_projects(project_id) ON DELETE SET NULL;


--
-- TOC entry 5045 (class 2606 OID 90128)
-- Name: research_projects fk_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.research_projects
    ADD CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 5041 (class 2606 OID 65743)
-- Name: loans loans_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.materials_items(item_id);


--
-- TOC entry 5042 (class 2606 OID 65748)
-- Name: loans loans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5029 (class 2606 OID 65580)
-- Name: materials materials_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id) ON DELETE SET NULL;


--
-- TOC entry 5033 (class 2606 OID 65638)
-- Name: materials_items materials_items_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.materials_items
    ADD CONSTRAINT materials_items_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(material_id) ON DELETE CASCADE;


--
-- TOC entry 5031 (class 2606 OID 65613)
-- Name: mentor_student mentor_student_mentor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mentor_student
    ADD CONSTRAINT mentor_student_mentor_id_fkey FOREIGN KEY (mentor_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 5032 (class 2606 OID 65618)
-- Name: mentor_student mentor_student_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mentor_student
    ADD CONSTRAINT mentor_student_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- TOC entry 5034 (class 2606 OID 65660)
-- Name: reservations reservations_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(material_id);


--
-- TOC entry 5035 (class 2606 OID 65655)
-- Name: reservations reservations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservations
    ADD CONSTRAINT reservations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5038 (class 2606 OID 65700)
-- Name: semantic_tags semantic_tags_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.semantic_tags
    ADD CONSTRAINT semantic_tags_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(material_id);


--
-- TOC entry 5030 (class 2606 OID 65596)
-- Name: user_interests user_interests_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_interests
    ADD CONSTRAINT user_interests_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 5202 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


-- Completed on 2026-04-26 05:33:10

--
-- PostgreSQL database dump complete
--

\unrestrict O7aCB2rHYr7gC7AqsJ39K2pYLIPcOXt92Qo0MtgljQhGokUWyZw87v7laiFBQ8u

